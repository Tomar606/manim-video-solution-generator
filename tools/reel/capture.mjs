// Frame capture for a reel's drawn footage: one Chromium, one page, every frame
// asked for by time.
//
//   import { capture } from '../../tools/reel/capture.mjs';
//   await capture({ html, dur: 11.4, out: 'clip.mp4' });               // a clip
//   await capture({ html, stills: [0, 5.7, 11.4], out: 'dir', name: 'turn' });  // PNGs
//
// The page contract (the same one docs/history-poc/map-d3/anim.mjs uses):
//   window.READY        a promise that resolves when the page can draw
//   window.frame(t, f)  draws the picture for time t (seconds) / frame f, and
//                       may return a promise
// The page is drawn at exactly 1080x1920 unless `size` says otherwise. Nothing
// here knows what is being drawn.
//
// A clip is H.264, yuv420p, crf 16, tagged BT.709, and is written to a
// temporary name and renamed when ffmpeg closes cleanly, so a file that exists
// is a file that finished.
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
// Playwright lives in tools/clip/node_modules and nowhere else; resolve it from
// there rather than moving or reinstalling it.
const require = createRequire(path.join(ROOT, 'tools/clip/package.json'));
const { chromium } = require('playwright');

const frameCount = (dur, fps) => Math.ceil(dur * fps - 1e-6);

export async function capture({
  html, out, dur = 0, fps = 30, size = [1080, 1920], stills = null, name = 'still',
  crf = 16, preset = 'medium', log = console.log,
}) {
  const [W, H] = size;
  const t0 = Date.now();
  const browser = await chromium.launch();
  let ff = null, tmp = null;
  try {
    const pg = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    const errors = [];
    pg.on('pageerror', e => { errors.push(e.message); console.error('pageerror:', e.message); });
    pg.on('console', m => { if (m.type() === 'error') console.error('page:', m.text()); });
    await pg.setContent(html, { waitUntil: 'load' });
    await pg.evaluate(() => window.READY);
    if (errors.length) throw new Error('the page threw while loading: ' + errors[0]);

    // PNG through CDP with optimizeForSpeed: lossless, and about twice as fast
    // as the default encoder on a full-frame canvas.
    const cdp = await pg.context().newCDPSession(pg);
    const shot = async () => Buffer.from((await cdp.send('Page.captureScreenshot',
      { format: 'png', optimizeForSpeed: true, captureBeyondViewport: false })).data, 'base64');
    const draw = (t, f) => pg.evaluate(([t, f]) => window.frame(t, f), [t, f]);

    if (stills) {
      fs.mkdirSync(out, { recursive: true });
      const files = [];
      for (const t of stills) {
        await draw(t, Math.round(t * fps));
        const file = path.join(out, `${name}_${t.toFixed(2)}.png`);
        fs.writeFileSync(file, await shot());
        files.push(file);
        log(`still ${name} t=${t.toFixed(2)}`);
      }
      return { files, seconds: (Date.now() - t0) / 1000 };
    }

    fs.mkdirSync(path.dirname(out), { recursive: true });
    tmp = out.replace(/\.mp4$/, '.part.mp4');
    ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps),
      '-c:v', 'png', '-i', '-',
      '-vf', 'scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p',
      '-c:v', 'libx264', '-preset', preset, '-crf', String(crf), '-pix_fmt', 'yuv420p',
      '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
      '-r', String(fps), '-movflags', '+faststart', tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
    const closed = new Promise((res, rej) => {
      ff.on('error', rej);
      ff.on('close', code => code === 0 ? res() : rej(new Error('ffmpeg exited ' + code)));
    });
    ff.stdin.on('error', () => {});          // the close handler reports the real failure
    const N = frameCount(dur, fps);
    for (let f = 0; f < N; f++) {
      await draw(f / fps, f);
      const buf = await shot();
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 30 === 0 || f === N - 1) log(`frame ${f + 1}/${N}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await closed;
    fs.renameSync(tmp, out);
    return { file: out, frames: N, seconds: (Date.now() - t0) / 1000 };
  } catch (e) {
    if (ff && ff.exitCode === null) ff.kill('SIGKILL');
    if (tmp && fs.existsSync(tmp)) fs.rmSync(tmp);
    throw e;
  } finally {
    await browser.close();
  }
}
