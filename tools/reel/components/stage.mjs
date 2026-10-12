// The timeline under a reel's drawing code: what every arts video's kit needs and
// none of them should write again. Promoted from work/pol-c3-la-02/design/kit.mjs
// (which stays as it is) when POL-C3-LA-05 became the second video to want it
// (PROCESS_ARTS.md section 6: a component earns tools/reel/ on its second use).
//
//   import { createStage } from '../../../tools/reel/components/stage.mjs';
//   const K = createStage({ video: VIDEO, slug: 'pol-c3-la-05' });
//   const { at, scope, dur } = K.load(1);           // scenes_part1.json + the word clock
//   K.item('t1', { at: 3.2, fx: 'pop' }); K.cue('knock', 3.2);
//   html += K.el({ at: 3.2, x: 40, y: 300 }, 'tag', 'शब्द', { fx: 'drop', cueKind: 'knock' });
//   await K.cli({ html: K.stage({ fontCSS, css, under, overlay: html, js, data }), part: 1, dur });
//
// What lives here: the registry (timeline items, sound cues), the fx engine that
// draws any item at absolute time t, the presenter's place and visibility per
// scene (look.json "place", a smoothstep glide centred on each cut), the page
// skeleton with its four layers, and the cli (layers, stills, cues, contact sheet).
// What does NOT: anything that decides how the video LOOKS. The video's kit gives
// the fonts, the CSS, the under layer's markup and its browser code
// (window.frameUnder(t), window.frame(t), optionally window.frameMask(t, pres)).
import fs from 'node:fs';
import path from 'node:path';
import { renderLayers, renderStills } from '../layers.mjs';
import { clock } from '../words.mjs';

const r3 = x => +(+x).toFixed(3);
export const dataURL = (f, mime) => fs.readFileSync(f).toString('base64').replace(/^/, `data:${mime};base64,`);

// fx and their default lengths (s)
export const FXD = { none: 0, fade: .2, press: .18, slam: .14, drop: .26, flip: .3, slideL: .3, slideR: .3, slideU: .3, slideD: .3, pop: .22, wipe: .35, draw: .35, grow: .4 };

export function createStage({ video, slug }) {
  const ROOT = path.resolve(video, '../..');
  const LOOK = JSON.parse(fs.readFileSync(path.join(video, 'look.json'), 'utf8'));
  const REG = { part: null, spec: null, out: null, items: [], cues: [], css: [], preload: [], n: 0 };
  const uid = p => `${p}${++REG.n}`;

  /** Read a part: scenes, the word clock, and at(sceneId, phrase, opts) scoped to that scene. */
  function load(part) {
    const spec = JSON.parse(fs.readFileSync(path.join(video, `scenes_part${part}.json`), 'utf8'));
    const S = Object.fromEntries(spec.scenes.map(s => [s.id, s]));
    const K = clock(path.join(ROOT, `work/${slug}/asr/aligned_part${part}.json`));
    const sc = id => { if (!S[id]) throw new Error(`no scene ${id} in part ${part}`); return S[id]; };
    const at = (id, phrase, o = {}) => K.at(phrase, { from: sc(id).t0, to: sc(id).t1, ...o });
    REG.part = part; REG.spec = spec;
    /** scope('s3'): later items default their `out` to that scene's end. */
    const scope = id => { const s = sc(id); REG.out = s.t1; return { id, t0: s.t0, t1: s.t1, len: s.t1 - s.t0, shots: s.shots, presenter: s.presenter, at: (p, o) => at(id, p, o) }; };
    return { part, spec, S, K, at, scope, dur: spec.dur };
  }

  /** A sound cue for tools/reel/audio.py. extra fields (e.g. n) pass through. */
  function cue(kind, t, dur = 0, extra = {}) {
    if (!Number.isFinite(t)) throw new Error(`cue ${kind}: time is not a number`);
    REG.cues.push({ kind, t: r3(t), dur: r3(dur), ...extra });
  }

  /** Put an element id on the timeline. out: undefined = end of the current scope, null = to the end of the part. */
  function item(id, o) {
    if (!Number.isFinite(o.at)) throw new Error(`item ${id}: "at" is not a number (${o.at})`);
    const fx = o.fx || 'fade';
    if (!(fx in FXD)) throw new Error(`item ${id}: unknown fx ${fx}`);
    REG.items.push({ id, at: r3(o.at), out: o.out === undefined ? REG.out : o.out === null ? null : r3(o.out), fx, d: o.d ?? FXD[fx], rot: o.rot || 0, hold: !!o.hold, len: o.len || 0 });
    return id;
  }
  const pos = o => {
    let s = '';
    if (o.cx) s += 'left:0;right:0;margin-left:auto;margin-right:auto;width:fit-content;';
    else if (o.x != null) s += `left:${o.x}px;`;
    if (o.right != null) s += `right:${o.right}px;`;
    if (o.y != null) s += `top:${o.y}px;`;
    if (o.w != null) s += `width:${o.w}px;`;
    if (o.h != null) s += `height:${o.h}px;`;
    return s + (o.style || '');
  };
  /** One positioned element on the timeline. */
  function el(o, cls, inner, { fx = 'fade', cueKind = null, rot = 0 } = {}) {
    const id = o.id || uid(cls.split(' ')[0]);
    item(id, { at: o.at, out: o.out, fx: o.fx || fx, rot: o.rot ?? rot, hold: o.hold, d: o.d });
    const k = o.cue === undefined ? cueKind : o.cue;
    if (k) cue(k, o.at);
    return `<div id="${id}" class="it ${cls} ${o.cls || ''}" style="${pos(o)}">${inner}</div>`;
  }
  /** An image as a CSS background (kept out of the DOM hash). Returns the class name. */
  function imageClass(file, fit = 'contain') {
    const cls = uid('im'), ext = path.extname(file).slice(1).replace('jpg', 'jpeg');
    REG.css.push(`.${cls}{background:url(${dataURL(path.isAbsolute(file) ? file : path.join(ROOT, file), 'image/' + ext)}) 50% 50%/${fit} no-repeat}`);
    REG.preload.push(cls);
    return cls;
  }

  /** The page. fontCSS/css: style; under/overlay: markup of those layers; js: browser code; data: JSON handed to it as D.v */
  function stage({ fontCSS = '', css = '', under = '', overlay = '', js = '', data = {}, fonts = [] }) {
    const D = {
      look: { place: LOOK.place, glide: LOOK.glide ?? .5, outd: LOOK.outd ?? .2 },
      scenes: REG.spec.scenes.map(s => ({ id: s.id, t0: s.t0, t1: s.t1, presenter: s.presenter, shots: s.shots.map(x => ({ clip: x.clip, t0: x.t0, t1: x.t1 })) })),
      items: REG.items, preload: REG.preload, fonts, v: data,
    };
    const pcrop = LOOK.pcrop, cut = path.join(video, 'assets/presenter_cutout.png');
    const pv = fs.existsSync(cut) ? `background:url(${dataURL(cut, 'image/png')}) 0 0/100% 100% no-repeat` : 'background:rgba(20,20,20,.55)';
    const C = LOOK.captions;
    return `<!doctype html><html><head><meta charset="utf-8"><style>${fontCSS}
html,body{margin:0;background:transparent}
#st{position:relative;width:1080px;height:1920px;overflow:hidden}
.layer{position:absolute;inset:0;display:none}
#L_mask{background:#000}#mk{position:absolute;inset:0;background:#fff}
#pv_pres{position:absolute;left:0;top:0;width:${pcrop.w}px;height:${pcrop.h}px;transform-origin:0 0;display:none;${pv}}
#pv_cap{position:absolute;left:40px;right:40px;top:${C.y0}px;height:${C.y1 - C.y0}px;border:3px dashed rgba(255,255,255,.45);box-sizing:border-box;display:none}
#pv_bg{background:#7d7d7d}
.it{position:absolute;opacity:0;visibility:hidden;box-sizing:border-box}
.sub{display:inline-block;opacity:0;visibility:hidden}
.svi{opacity:0;visibility:hidden}
${REG.css.join('')}${css}</style></head><body>
<div id="st">
 <div id="pv_bg" class="layer"></div>
 <div id="L_under" class="layer">${under}</div>
 <div id="L_mask" class="layer"><div id="mk"></div></div>
 <div id="pv_pres"></div>
 <div id="L_overlay" class="layer">${overlay}</div>
 <div id="pv_cap"></div>
</div>
<script>(${ENGINE.toString()})(${JSON.stringify(D)});${js}</script></body></html>`;
  }

  const zoomed = (html, z) => html.replace('</style>', `html{zoom:${z}}</style>`);
  /** node partN.mjs [--workers n] | --stills t1,t2 [--layer preview] [--full] | --cues | --sheet */
  async function cli({ html, part, dur }) {
    const a = process.argv.slice(2), out = path.join(video, 'out'), opt = k => { const i = a.indexOf(k); return i < 0 ? null : a[i + 1]; };
    if (a.includes('--cues')) {
      const seen = new Set(), list = REG.cues.slice().sort((x, y) => x.t - y.t || x.kind.localeCompare(y.kind)).filter(c => { const k = c.kind + ':' + c.t.toFixed(2); if (seen.has(k) || c.t >= dur) return false; seen.add(k); return true; });
      const f = path.join(out, `cues_p${part}.json`);
      fs.mkdirSync(out, { recursive: true });
      fs.writeFileSync(f, '[\n' + list.map(c => ' ' + JSON.stringify(c)).join(',\n') + '\n]\n');
      console.log(`${list.length} cues -> ${f}`);
      return;
    }
    if (a.includes('--stills')) {
      const times = opt('--stills').split(',').map(Number), layers = (opt('--layer') || 'preview').split(','), full = a.includes('--full');
      await renderStills({ html: full ? html : zoomed(html, .5), outDir: path.join(out, `stills/p${part}`), times, layers, size: full ? [1080, 1920] : [540, 960] });
      return;
    }
    if (a.includes('--sheet')) {
      const sc = REG.spec.scenes, shots = [];
      sc.forEach((s, i) => { if (i) shots.push({ t: +(s.t0 + .3).toFixed(2), lb: `${s.id} +0.3` }); shots.push({ t: +((s.t0 + s.t1) / 2).toFixed(2), lb: `${s.id} mid · ${s.presenter}` }); });
      const tmp = path.join(out, `stills/p${part}/.sheet`), tw = 270, th = 480, cols = 9, rows = Math.ceil(shots.length / cols);
      const files = await renderStills({ html: zoomed(html, tw / 1080), outDir: tmp, times: shots.map(s => s.t), layers: ['preview'], size: [tw, th], log: () => { } });
      const cells = shots.map((s, i) => `<div class="c"><img src="${dataURL(files[i], 'image/png')}"><b>${s.lb} · ${s.t.toFixed(1)}s</b></div>`).join('');
      const Wp = cols * (tw + 8) + 8, Hp = rows * (th + 34) + 8;
      const page = `<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#222}#st{width:${Wp}px;height:${Hp}px;display:flex;flex-wrap:wrap;gap:8px;padding:8px;box-sizing:border-box;align-content:flex-start}.c{width:${tw}px}.c img{display:block;width:${tw}px;height:${th}px}.c b{display:block;font:600 15px/26px sans-serif;color:#eee}</style><div id="st">${cells}</div><script>window.render=()=>{}</script>`;
      const [f] = await renderStills({ html: page, outDir: tmp, times: [0], layers: ['sheet'], size: [Wp, Hp], log: () => { } });
      const dst = path.join(out, `stills/p${part}/sheet_p${part}.png`);
      fs.renameSync(f, dst); fs.rmSync(tmp, { recursive: true, force: true });
      console.log(`sheet: ${shots.length} frames -> ${dst}`);
      return;
    }
    const stats = await renderLayers({ html, outDir: path.join(out, `layers/p${part}`), dur, layers: ['under', 'mask', 'overlay'], fps: LOOK.fps || 30, workers: +(opt('--workers') || 3) });
    console.log(JSON.stringify(stats));
  }

  return { LOOK, ROOT, REG, uid, load, cue, item, el, pos, imageClass, stage, cli, dataURL };
}

// ------------------------------------------------------------- engine ----
// Runs in the browser. Everything is a pure function of t, so any page can draw any frame.
function ENGINE(D) {
  const $ = id => document.getElementById(id);
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const P = (t, a, b) => b <= a ? (t >= a ? 1 : 0) : clamp((t - a) / (b - a));
  const eout = p => 1 - Math.pow(1 - p, 3), ein = p => p * p * p;
  const eio = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
  const eback = p => { const c = 1.70158, q = p - 1; return 1 + (c + 1) * q * q * q + c * q * q; };
  const lerp = (a, b, p) => a + (b - a) * p;
  const f1 = x => String(Math.round(x * 10) / 10), f2 = x => String(Math.round(x * 100) / 100), f3 = x => String(Math.round(x * 1000) / 1000);
  const rgb = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
  const mix = (c1, c2, p) => { const a = rgb(c1), b = rgb(c2); return 'rgb(' + a.map((v, i) => Math.round(lerp(v, b[i], p))).join(',') + ')'; };
  const SC = D.scenes, OUTD = D.look.outd || .2;   // how long an item takes to fade out (look.json "outd")
  const sceneAt = t => { let i = 0; while (i < SC.length - 1 && t >= SC[i].t1) i++; return i; };
  /** env(t,a,b,din,dout): 0 outside a..b, eased 0→1 after a and 1→0 before b */
  const env = (t, a, b, din = .2, dout = .2) => t < a || (b != null && t >= b) ? 0 : Math.min(P(t, a, a + din), b == null ? 1 : 1 - P(t, b - dout, b));
  function runItems(t) {
    for (const it of D.items) {
      const e = $(it.id); if (!e) continue;
      if (t < it.at - 1e-6 || (it.out != null && t >= it.out - 1e-6)) { e.style.visibility = 'hidden'; e.style.opacity = '0'; continue; }
      const p = it.d > 0 ? clamp((t - it.at) / it.d) : 1, q = it.out == null || it.hold ? 1 : clamp((it.out - t) / OUTD);
      let o = 1, tf = '';
      switch (it.fx) {
        case 'fade': o = p; break;
        case 'press': o = clamp(p * 3); tf = 'scale(' + f3(1.08 - .08 * eout(p)) + ')'; break;
        case 'slam': o = clamp(p * 2.5); tf = 'scale(' + f3(1.9 - .9 * p * p) + ')'; break;
        case 'drop': o = clamp(p * 3); tf = 'translateY(' + f1(-26 * (1 - eout(p))) + 'px) scale(' + f3(1.12 - .12 * ein(p)) + ')'; break;
        case 'flip': o = clamp(p * 4); tf = 'perspective(900px) rotateX(' + f1(-90 * (1 - eout(p))) + 'deg)'; break;
        case 'slideL': o = clamp(p * 2.5); tf = 'translateX(' + f1(-90 * (1 - eout(p))) + 'px)'; break;
        case 'slideR': o = clamp(p * 2.5); tf = 'translateX(' + f1(90 * (1 - eout(p))) + 'px)'; break;
        case 'slideU': o = clamp(p * 2.5); tf = 'translateY(' + f1(70 * (1 - eout(p))) + 'px)'; break;
        case 'slideD': o = clamp(p * 2.5); tf = 'translateY(' + f1(-70 * (1 - eout(p))) + 'px)'; break;
        case 'pop': o = clamp(p * 3); tf = 'scale(' + f3(.4 + .6 * eback(p)) + ')'; break;
        case 'grow': o = clamp(p * 4); tf = 'scaleX(' + f3(eout(p)) + ')'; break;
        case 'wipe': e.style.clipPath = p >= 1 ? 'none' : 'inset(0 ' + f1(100 * (1 - eout(p))) + '% 0 0)'; break;
        case 'draw': e.style.strokeDashoffset = f1(it.len * (1 - eout(p))); break;
      }
      e.style.visibility = 'visible'; e.style.opacity = f3(o * q);
      if (tf || it.rot) e.style.transform = tf + (it.rot ? ' rotate(' + it.rot + 'deg)' : '');
    }
  }
  // the presenter: place (glide centred on the cut) and visibility
  const PL = D.look.place;
  const seen = i => SC[i].presenter === 'hidden' ? 0 : 1;
  const placeOf = i => { for (const j of [i, i + 1, i - 1, i + 2, i - 2]) if (SC[j] && SC[j].presenter !== 'hidden') return PL[SC[j].presenter]; return PL.you; };
  /** Interpolate any per-state value across cuts with the presenter's own glide. of(state) -> number or {k: number}. */
  function glide(t, of) {
    const i = sceneAt(t), s = SC[i], g = D.look.glide / 2;
    const val = j => of(SC[j].presenter, SC[j]);
    let a = val(i), b = a, p = 0;
    if (i > 0 && t - s.t0 < g) { b = a; a = val(i - 1); p = eio(.5 + (t - s.t0) / (2 * g)); }
    else if (i < SC.length - 1 && s.t1 - t < g) { b = val(i + 1); p = eio(.5 - (s.t1 - t) / (2 * g)); }
    if (typeof a === 'number') return lerp(a, b, p);
    const o = {}; for (const k in a) o[k] = lerp(a[k], b[k], p); return o;
  }
  function pres(t) {
    const i = sceneAt(t), s = SC[i], m = .125;
    let v = seen(i);
    if (i > 0 && t - s.t0 < m) v = lerp(seen(i - 1), v, .5 + (t - s.t0) / (2 * m));
    else if (i < SC.length - 1 && s.t1 - t < m) v = lerp(v, seen(i + 1), .5 - (s.t1 - t) / (2 * m));
    const g = glide(t, (st, sc) => { const j = SC.indexOf(sc); const q = placeOf(j); return { s: q.s, x: q.x0, y: q.y0 }; });
    return { v, s: g.s, x: g.x, y: g.y, state: s.presenter, scene: s };
  }
  function hash(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193); } return (h >>> 0).toString(36) + ':' + s.length; }
  const SHOW = { under: ['L_under'], mask: ['L_mask'], overlay: ['L_overlay'], preview: ['pv_bg', 'L_under', 'pv_pres', 'L_overlay', 'pv_cap'] };
  const ALL = ['pv_bg', 'L_under', 'L_mask', 'pv_pres', 'L_overlay', 'pv_cap'];
  window.frameKey = layer => hash((SHOW[layer] || []).map(id => $(id).outerHTML).join(''));
  window.render = (t, layer) => {
    const show = SHOW[layer] || [];
    for (const id of ALL) $(id).style.display = show.includes(id) ? 'block' : 'none';
    if ((layer === 'under' || layer === 'preview') && window.frameUnder) window.frameUnder(t);
    if (layer === 'mask') { const p = pres(t); $('mk').style.opacity = f3(p.v); if (window.frameMask) window.frameMask(t, p); }
    if (layer === 'overlay' || layer === 'preview') { runItems(t); if (window.frame) window.frame(t); }
    if (layer === 'preview') { const p = pres(t); $('pv_pres').style.opacity = f3(p.v); $('pv_pres').style.transform = 'translate(' + f1(p.x) + 'px,' + f1(p.y) + 'px) scale(' + f3(p.s) + ')'; if (window.framePreview) window.framePreview(t, p); }
  };
  const pre = (D.preload || []).map(c => { const r = [...document.styleSheets[0].cssRules].find(r => r.selectorText === '.' + c); const u = /url\(([^)]+)\)/.exec(r.style.backgroundImage.replace(/"/g, '')); const im = new Image(); im.src = u[1]; return im.decode().catch(() => { }); });
  window.READY = Promise.all([...pre, ...(D.fonts || []).map(f => document.fonts.load(f, 'कख 12 ab'))]);
  Object.assign(window, { $, clamp, P, eout, ein, eio, eback, lerp, f1, f2, f3, mix, SC, env, sceneAt, pres, glide, D });
}
