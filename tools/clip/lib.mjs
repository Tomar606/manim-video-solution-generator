/* lib.mjs — what every tools/clip script shares.
 *
 * THE ONE RENDERER. Until this existed, every video folder under work/ carried
 * its own copy of the engine and the scripts that drive it: nine copies of
 * full.mjs in six versions, nine of engine.js in seven. A fix made in one
 * folder never reached the next, and each new video inherited the LAST video's
 * design along with its code — BIO-C2-LA-01 rendered over chemistry test tubes
 * because the full.mjs it copied defaulted to the chemistry plate.
 *
 * So the process lives here, once, and a video folder holds only design:
 *
 *   work/<slug>/video.json      background (required), subject, question, year
 *   work/<slug>/theme.css       optional overrides of engine/style.css
 *   work/<slug>/spec/           segments_part<N>.json and the design it is built from
 *   work/<slug>/assets/         the plate, the SVGs, the question sheet
 *   work/<slug>/out/            everything generated
 *
 * The page the engine renders is served as ONE site stitched from two places:
 *   /renderer/*            -> tools/clip/engine/          (process)
 *   /renderer/video.css    -> generated: --plate from video.json + theme.css
 *   everything else        -> work/<slug>/                (design + output)
 *   /assets/* not found    -> the repo's assets/          (shared furniture: the torn divider)
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

export const CLIP = path.dirname(fileURLToPath(import.meta.url));
export const REPO = path.resolve(CLIP, '..', '..');
export const ENGINE = path.join(CLIP, 'engine');
export const FPS = 30, W = 1080, H = 1920;

export function die(msg) { console.error(msg); process.exit(1); }

/* --flag value | --flag=value | --flag (boolean). Only these take a value, so a
   boolean flag can never swallow the positional after it. */
const VALUED = new Set(['part', 'spec', 'out', 'segs', 'dur', 't', 'pages', 'port']);
export function parseArgs(argv = process.argv.slice(2)) {
  const a = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const x = argv[i];
    if (!x.startsWith('--')) { a._.push(x); continue; }
    const [k, v] = x.slice(2).split(/=(.*)/s);
    if (v !== undefined) a[k] = v;
    else if (VALUED.has(k)) { if (i + 1 >= argv.length) die(`--${k} needs a value`); a[k] = argv[++i]; }
    else a[k] = true;
  }
  return a;
}

/* <slug> means work/<slug>; anything containing a slash is a path. */
export function videoDir(ref) {
  if (!ref) die('first argument: the video — a slug (che-c3-sa-06) or a folder path');
  const dir = ref.includes('/') ? path.resolve(ref) : path.join(REPO, 'work', ref);
  if (!fs.existsSync(dir)) die(`no video folder: ${dir}\nstart one with: python3 tools/build_clip.py <QID> init`);
  return dir;
}

/* THE VIDEO FOLDER HOLDS NO CODE. A folder that carries its own engine.js or
   full.mjs is running its own fork of the process, and editing that copy while
   this one renders is how a fix "doesn't take". Old folders under work/ are
   the records of shipped videos and keep their copies; they are not built by
   these tools unless CLIP_ALLOW_CODE=1 says so on purpose. */
export function codeIn(dir) {
  const hits = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.isFile() && /\.(mjs|js|cjs|py|sh)$/.test(e.name)) hits.push(e.name);
    if (e.name === 'node_modules') hits.push('node_modules/');
  }
  const r = path.join(dir, 'renderer');
  if (fs.existsSync(r))
    for (const n of fs.readdirSync(r)) if (/\.(m?js|html)$/.test(n)) hits.push(`renderer/${n}`);
  return hits;
}

/* The file a design path names: the video folder first, then the repo (so
   video.json may point at a shared plate such as assets/backgrounds/…). */
export function designFile(dir, rel) {
  for (const base of [dir, REPO]) {
    const p = path.join(base, rel);
    if (fs.existsSync(p)) return p;
  }
  return null;
}

export function loadVideo(dir) {
  const code = codeIn(dir);
  if (code.length && process.env.CLIP_ALLOW_CODE !== '1')
    die(`${path.relative(REPO, dir)} carries its own copy of the process: ${code.join(', ')}\n` +
        `A video folder holds design only (PROCESS.md). Use that folder's own scripts, ` +
        `or set CLIP_ALLOW_CODE=1 to render it with tools/clip on purpose.`);
  const cfgPath = path.join(dir, 'video.json');
  if (!fs.existsSync(cfgPath))
    die(`no video.json in ${path.relative(REPO, dir)}\n` +
        `it names the background; start the folder with: python3 tools/build_clip.py <QID> init`);
  const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  // NO DEFAULT BACKGROUND. A default is how one subject's plate ends up under
  // another subject's video; a missing file used to render onto a black frame.
  if (!cfg.background) die(`video.json has no "background"`);
  if (!designFile(dir, cfg.background))
    die(`background not found: ${cfg.background}\nput the plate there or fix video.json. ` +
        `Rendering without it gives a black frame.`);
  return { ...cfg, dir };
}

/* Which spec: --spec <path> | --part N | spec/segments.json. Parts never share
   a file: copying part N over segments.json while part M was starting up once
   rendered the wrong part's segments under the right part's name. */
export function specOf(dir, a) {
  const rel = a.spec ? a.spec
            : a.part ? `spec/segments_part${a.part}.json`
            : 'spec/segments.json';
  const abs = path.resolve(dir, rel);
  if (!abs.startsWith(dir + path.sep)) die(`--spec must be inside the video folder: ${rel}`);
  if (!fs.existsSync(abs)) die(`no spec: ${path.relative(REPO, abs)}`);
  let segs = JSON.parse(fs.readFileSync(abs, 'utf8'));
  if (a.segs) {
    const want = new Set(String(a.segs).split(',').map(Number));
    segs = segs.filter(s => want.has(s.seg_id));
    if (!segs.length) die(`no segments matched: ${a.segs}`);
  }
  return { rel: path.relative(dir, abs), abs, segs };
}

/* out/<name> with the part folded in:  render-part2.mp4, tiles_part2/ … */
export function outPath(dir, a, base, ext = '') {
  if (a.out) return path.resolve(dir, a.out);
  return path.join(dir, 'out', `${base}${a.part ? `-part${a.part}` : ''}${ext}`);
}

export const sha = buf => crypto.createHash('sha256').update(buf).digest('hex').slice(0, 16);

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp' };

function inside(root, rel) {
  const p = path.join(root, rel);
  return p === root || p.startsWith(root + path.sep) ? p : null;
}

export function videoCss(cfg) {
  let css = `/* generated by tools/clip/lib.mjs from video.json + theme.css */\n` +
            `:root{--plate:url('/${encodeURI(cfg.background)}')}\n`;
  const theme = path.join(cfg.dir, 'theme.css');
  if (fs.existsSync(theme)) css += fs.readFileSync(theme, 'utf8');
  return css;
}

export function serve(cfg, port = 0) {
  const s = http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '');
    const send = (type, buf) => {
      res.writeHead(200, { 'content-type': type, 'cache-control': 'no-store' });
      res.end(buf);
    };
    if (rel === 'renderer/video.css') return send('text/css', videoCss(cfg));
    let file = rel.startsWith('renderer/') ? inside(ENGINE, rel.slice('renderer/'.length))
                                           : inside(cfg.dir, rel || 'renderer/index.html');
    if (file && !fs.existsSync(file) && !rel.startsWith('renderer/')) {
      const shared = inside(REPO, rel);
      if (shared && (rel.startsWith('assets/')) && fs.existsSync(shared)) file = shared;
    }
    if (!file) { res.writeHead(403).end(); return; }
    fs.readFile(file, (err, buf) => {
      if (err) { res.writeHead(404).end('not found: ' + rel); return; }
      send(TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream', buf);
    });
  });
  return new Promise(r => s.listen(port, '127.0.0.1', () => r({ server: s, port: s.address().port })));
}

export async function launch() {
  const { chromium } = await import('playwright');
  return chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
}

export async function newPage(browser, w = W, h = H) {
  return browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
}

/* The engine page, headless, on the given spec. `seg` preloads that index. */
export async function openEngine(page, port, specRel, seg = null) {
  const q = new URLSearchParams({ headless: '1', spec: specRel });
  if (seg != null) q.set('seg', String(seg));
  await page.goto(`http://127.0.0.1:${port}/renderer/index.html?${q}`, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.READY === true, null, { timeout: 30000 });
  await page.evaluate(() => document.fonts.ready);
}

/* Bake the plate straight onto #frame, exactly as full.mjs always has, so a
   preview frame is the delivered frame. */
export async function bakePlate(page, bg) {
  await page.evaluate(bg => {
    const f = document.getElementById('frame');
    f.style.background = `#000 url('../${bg}') center/cover no-repeat`;
    document.body.style.background = '#000';
  }, bg);
}

/* the text audit: everything the spec promises must be in the DOM, verbatim */
export async function textAudit(page, seg) {
  const onScreen = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('#caption .phrase, #stage .lbl, #eqWrap .eqarc')
      .forEach(e => out.push(e.textContent));
    document.querySelectorAll('#eq .katex-mathml annotation').forEach(e => out.push(e.textContent));
    return out;
  });
  // engine.js swaps in U+2011 (non-breaking hyphen) and U+2060 (word joiner) so
  // "d-block" and Devanagari compounds never split across caption lines
  const norm = s => s.replace(/‑/g, '-').replace(/⁠/g, '');
  const seen = onScreen.map(norm);
  return [...(seg.phrases || []).map(p => p.text),
          ...(seg.labels || []).map(l => l.text),
          ...((seg.equation && seg.equation.arcs) || []).map(a => a.label)]
    .filter(t => !seen.includes(norm(t)));
}

/* ---------------------------------------------------------------- the question card
 * Each entry: [layer, t_in, dur, motion]. The order is the order the approved
 * Manim scene stages them in - ring, heading, sparks lagging the word they
 * belong to, rule drawing, sheet dropping, tape popping onto it, badge, then
 * the pill rising last. Nothing moves after 2.6s. The layers are full-frame
 * RGBA pngs from make_intro_layers.py; the card is opaque down to CARD_H (the
 * presenter's floor) and does nothing below it. */
export const INTRO_PLAN = [
  ['ring',       0.15, 0.45, 'grow'],
  ['head',       0.35, 0.50, 'up'],
  ['sparks',     0.72, 0.40, 'pop'],
  ['rule',       0.62, 0.55, 'draw'],
  ['sheet',      0.95, 0.60, 'drop'],
  ['tape',       1.45, 0.32, 'pop'],
  ['badge',      1.62, 0.42, 'pop'],
  ['pill',       1.88, 0.55, 'rise'],
  ['pillsparks', 2.22, 0.35, 'pop'],
];
export const CARD_H = 1344;
export const CARD_FADE = 0.5;

/* The browser half of the card: installs window.CARD_SET(t), which poses every
 * layer at card time t. Shared by intro.mjs (the card as its own video) and
 * full.mjs --intro (the card drawn into the render's own frames). Serialised
 * into the page, so it must not close over anything. */
export function cardPoser(plan, idOf) {
  const ease = u => 1 - Math.pow(1 - u, 3);                  // ease-out cubic
  const back = u => { const c = 1.70158 + 1;                  // slight overshoot
    return 1 + c * Math.pow(u - 1, 3) + 1.70158 * Math.pow(u - 1, 2); };
  window.CARD_SET = t => {
    for (const [name, tin, dur, motion] of plan) {
      const el = document.getElementById(idOf + name);
      const u = Math.max(0, Math.min(1, (t - tin) / dur));
      const e = ease(u), b = back(u);
      let tf = '', op = e;
      if (motion === 'grow') tf = `scale(${(0.72 + 0.28 * b).toFixed(4)})`;
      else if (motion === 'up')   tf = `translateY(${(36 * (1 - e)).toFixed(2)}px)`;
      else if (motion === 'pop')  tf = `scale(${(0.55 + 0.45 * b).toFixed(4)})`;
      else if (motion === 'drop') tf = `translateY(${(-74 * (1 - e)).toFixed(2)}px)`;
      else if (motion === 'rise') tf = `translateY(${(58 * (1 - e)).toFixed(2)}px)`;
      else if (motion === 'draw') {
        // the rule draws outward from its centre: a clip that opens both ways,
        // which is what a hand sweeping a line under a heading looks like
        const half = 50 * e;
        el.style.clipPath = `inset(0 ${(50 - half).toFixed(2)}% 0 ${(50 - half).toFixed(2)}%)`;
        op = u > 0 ? 1 : 0;
      }
      el.style.opacity = op.toFixed(4);
      if (tf) el.style.transform = tf;
    }
  };
}

/* Lay the card INTO an engine page: window.CARD(t) poses it at part time t —
 * opaque from frame 0 (NO fade in: it covers the captions and stage under it),
 * dissolving out over the last CARD_FADE seconds of `dur`, gone from `dur` on.
 * This is exactly what the separate overlay pass did
 * (fade=t=out:st=dur-0.5:d=0.5:alpha=1, enable lt(t,dur)), minus one whole
 * re-encode of the part and one generation of compression on the card. */
export async function installCard(page, port, dur) {
  const base = `http://127.0.0.1:${port}`;
  const broken = await page.evaluate(async ({ plan, base, H }) => {
    const wrap = document.createElement('div');
    wrap.id = 'introCard';
    wrap.style.cssText = `position:fixed;left:0;top:0;width:1080px;height:${H}px;overflow:hidden;` +
                         'z-index:2147483647;pointer-events:none;display:none';
    const add = (id, src, op) => {
      const i = new Image();
      i.id = id; i.src = src;
      i.style.cssText = 'position:absolute;left:0;top:0;width:1080px;height:1920px;' +
                        `transform-origin:50% 50%;will-change:transform,opacity;opacity:${op}`;
      wrap.appendChild(i);
    };
    add('card_plate', `${base}/out/plate.png`, 1);
    for (const [n] of plan) add('card_' + n, `${base}/out/layers/${n}.png`, 0);
    document.body.appendChild(wrap);
    // decode() rather than complete: a broken image is also "complete", and a
    // card whose layers failed renders as a silent black band
    await Promise.all([...wrap.querySelectorAll('img')].map(i => i.decode().catch(() => {})));
    return [...wrap.querySelectorAll('img')].filter(i => !i.naturalWidth).map(i => i.id);
  }, { plan: INTRO_PLAN, base, H: CARD_H });
  if (broken.length) die(`card layers failed to load: ${broken.join(', ')} — run the card step first`);
  await page.evaluate(`(${cardPoser.toString()})(${JSON.stringify(INTRO_PLAN)}, 'card_')`);
  await page.evaluate(({ dur, fade }) => {
    const wrap = document.getElementById('introCard');
    window.CARD = t => {
      if (t >= dur) { wrap.style.display = 'none'; return; }
      wrap.style.display = 'block';
      wrap.style.opacity = Math.max(0, Math.min(1, (dur - t) / fade)).toFixed(4);
      window.CARD_SET(t);
    };
  }, { dur, fade: CARD_FADE });
}
