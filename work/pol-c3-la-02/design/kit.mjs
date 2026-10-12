// POL-C3-LA-02 "दो स्याही": the ONE definition of the look. Every part imports this.
// API and a usage example: KIT.md (next to this file). This file may only DRAW:
// timing comes from tools/reel/words.mjs, rendering from tools/reel/layers.mjs.
//
// How it works: the functions below run in Node. Each returns an HTML string and
// REGISTERS what it needs (a timeline item, a sound cue, a state of THE LINE).
// stage() serialises the registry into the page, where ENGINE() (below, run in
// the browser) draws any frame from absolute time t.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderLayers, renderStills } from '../../../tools/reel/layers.mjs';
import { clock } from '../../../tools/reel/words.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const VIDEO = path.resolve(HERE, '..');
export const ROOT = path.resolve(HERE, '../../..');
export const LOOK = JSON.parse(fs.readFileSync(path.join(VIDEO, 'look.json'), 'utf8'));
export const dataURL = (f, mime) => `data:${mime};base64,${fs.readFileSync(path.isAbsolute(f) ? f : path.join(ROOT, f)).toString('base64')}`;
const r3 = x => +(+x).toFixed(3);

// ------------------------------------------------------------ registry ----
const REG = { part: null, spec: null, out: null, items: [], cues: [], wash: [], css: [], n: 0, line: null };
const uid = p => `${p}${++REG.n}`;

/** Read a part: scenes, the word clock, and at(sceneId, phrase, opts) scoped to that scene. */
export function load(part) {
  const spec = JSON.parse(fs.readFileSync(path.join(VIDEO, `scenes_part${part}.json`), 'utf8'));
  const S = Object.fromEntries(spec.scenes.map(s => [s.id, s]));
  const K = clock(`work/pol-c3-la-02/asr/aligned_part${part}.json`);
  const sc = id => { if (!S[id]) throw new Error(`no scene ${id} in part ${part}`); return S[id]; };
  const at = (id, phrase, o = {}) => K.at(phrase, { from: sc(id).t0, to: sc(id).t1, ...o });
  REG.part = part; REG.spec = spec;
  /** scope('s3'): later components default their `out` to that scene's end; returns {t0,t1,len,at(phrase,o)}. */
  const scope = id => { const s = sc(id); REG.out = s.t1; return { id, t0: s.t0, t1: s.t1, len: s.t1 - s.t0, shots: s.shots, at: (p, o) => at(id, p, o) }; };
  return { part, spec, S, K, at, scope, dur: spec.dur };
}

/** A sound cue. kinds: slide | stamp | scratch | tick | flip | drop. */
export function cue(kind, t, dur = 0) {
  if (!Number.isFinite(t)) throw new Error(`cue ${kind}: time is not a number`);
  REG.cues.push({ kind, t: r3(t), dur: r3(dur) });
}

const FXD = { none: 0, fade: .2, press: .18, slam: .14, slideL: .3, slideR: .3, slideU: .3, slideD: .3, pop: .22, wipe: .35, draw: .35 };
/** Put an element id on the timeline. fx: none fade press slam slideL slideR slideU slideD pop wipe draw(len). */
export function item(id, o) {
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
// one positioned element on the timeline
function el(o, cls, inner, { fx = 'fade', cueKind = null, rot = 0 } = {}) {
  const id = o.id || uid(cls.split(' ')[0]);
  item(id, { at: o.at, out: o.out, fx: o.fx || fx, rot: o.rot ?? rot, hold: o.hold, d: o.d });
  const k = o.cue === undefined ? cueKind : o.cue;
  if (k) cue(k, o.at);
  return `<div id="${id}" class="it ${cls} ${o.ink || ''} ${o.cls || ''}" style="${pos(o)}">${inner}</div>`;
}

// ---------------------------------------------------------- components ----
/** Anything of yours on the timeline. box(html, {at, out, x, y, w, h, cx, fx, rot, cue, ink, cls, style, id}) */
export const box = (html, o) => el(o, 'bx', html, {});

/** A line of type. font: head (Khand) | body (Mukta) | serif (Tiro). ink: ink | red | blue. */
export function text(o) {
  const f = { head: `700 ${o.size || 64}px/1.2 Khand,Mukta`, body: `800 ${o.size || 44}px/1.3 Mukta`, serif: `400 ${o.size || 56}px/1.45 Tiro,Mukta` }[o.font || 'head'];
  return el({ ...o, ink: o.ink || 'ink', style: `font:${f};${o.wrap ? '' : 'white-space:nowrap;'}${o.style || ''}` }, 'tx', o.html, { fx: o.fx || 'press' });
}

/** Poster heading, stamped on. n / year / text are each optional; atYear / atText default to at. size: 'big' | 'band' (one row, for the y 1040-1175 band). */
export function heading(o) {
  const id = o.id || uid('hd'), band = o.size === 'band';
  const sub = (k, html, t) => {
    if (html == null) return '';
    item(`${id}_${k}`, { at: t ?? o.at, out: o.out, fx: 'press' }); cue('stamp', t ?? o.at);
    return `<span id="${id}_${k}" class="sub hd${k}">${html}</span>`;
  };
  item(id, { at: Math.min(o.at, o.atYear ?? o.at, o.atText ?? o.at), out: o.out, fx: 'none' });
  const row = sub('n', o.n, o.at) + sub('y', o.year, o.atYear), txt = sub('t', o.text, o.atText);
  return `<div id="${id}" class="it hd ${band ? 'band' : ''} ${o.ink || 'ink'}" style="${pos(o)}">${band ? row + txt : `<div class="hdr">${row}</div>${txt}`}</div>`;
}

/** A "यानी" margin note on a pinned paper slip. from: 'L' | 'R' | 'U' | 'D' (side it slides in from). */
export const slip = o => el({ ...o, style: `${o.size ? `font-size:${o.size}px;` : ''}${o.style || ''}` }, 'sl', `<i class="pin"></i>${o.html ?? o.text}`, { fx: 'slide' + (o.from || 'L'), cueKind: 'slide', rot: -2 });

/** A rubber stamp that slams in. size = font px (default 84). */
export const stamp = o => el({ ...o, ink: o.ink || 'ink', style: `font-size:${o.size || 84}px;${o.style || ''}` }, 'sp', o.html ?? o.text, { fx: 'slam', cueKind: 'stamp', rot: -6 });

const POINT_INK = ['blue', 'red', 'blue', 'blue', 'blue', 'blue'];   // whose point each of the six is
/** Six point-pips. fill: [t|null x n] when each fills; filled: how many are full from the start. Default place: top right of the strip. */
export function pips(o) {
  const id = o.id || uid('pp'), n = o.n || 6, sz = o.size || 26, inks = o.inks || POINT_INK;
  let h = '';
  for (let i = 0; i < n; i++) {
    let f = '';
    const t = i < (o.filled || 0) ? o.at : (o.fill || [])[i];
    if (t != null) { item(`${id}_${i}`, { at: t, out: o.out, fx: t === o.at ? 'none' : 'pop' }); if (t !== o.at) cue('tick', t); f = `<i id="${id}_${i}" class="pipf ${inks[i]}"></i>`; }
    h += `<i class="pip" style="width:${sz}px;height:${sz}px">${f}</i>`;
  }
  return el({ x: 824, y: 66, ...o, id, style: `gap:${Math.round(sz * .4)}px;${o.style || ''}` }, 'pp', h, {});
}

const SYM = {
  crown: `<path d="M12 74 L5 28 L29 48 L50 14 L71 48 L95 28 L88 74 Z"/><rect x="12" y="80" width="76" height="11" rx="2"/><circle cx="5" cy="24" r="6"/><circle cx="50" cy="10" r="6"/><circle cx="95" cy="24" r="6"/>`,
  book: `<path d="M50 24 C38 13 20 13 5 19 V84 C20 78 38 78 50 89 C62 78 80 78 95 84 V19 C80 13 62 13 50 24 Z"/><path d="M50 26 V87 M15 34 C24 31 34 32 42 37 M15 48 C24 45 34 46 42 51 M15 62 C24 59 34 60 42 65 M85 34 C76 31 66 32 58 37 M85 48 C76 45 66 46 58 51 M85 62 C76 59 66 60 58 65" fill="none" stroke="var(--paper)" stroke-width="3.5" stroke-linecap="round"/>`,
  tick: `<path d="M12 54 L38 80 L88 20" fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>`,
  cross: `<path d="M18 18 L82 82 M82 18 L18 82" fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="round"/>`,
  people: `<circle cx="24" cy="30" r="12"/><path d="M4 86 V66 Q4 48 24 48 Q44 48 44 66 V86 Z"/><circle cx="76" cy="30" r="12"/><path d="M56 86 V66 Q56 48 76 48 Q96 48 96 66 V86 Z"/><circle cx="50" cy="22" r="13"/><path d="M28 90 V62 Q28 42 50 42 Q72 42 72 62 V90 Z" stroke="var(--paper)" stroke-width="3"/>`,
};
/** A flat symbol in its ink. Plain inline SVG (no timeline) unless `at` is given. names: crown book tick cross people. */
export function sym(name, o = {}) {
  if (!SYM[name]) throw new Error(`no symbol ${name}`);
  const sz = o.size || 100;
  const svg = `<svg class="sy ${o.at == null ? (o.ink || '') : ''}" ${o.at == null && o.id ? `id="${o.id}"` : ''} width="${sz}" height="${sz}" viewBox="0 0 100 100" fill="currentColor" style="${o.at == null ? (o.style || '') : ''}">${SYM[name]}</svg>`;
  return o.at == null ? svg : el({ ...o, ink: o.ink || 'ink' }, 'bx', svg, { fx: 'pop' });
}
export const crown = (o = {}) => sym('crown', { ink: 'red', ...o });
export const book = (o = {}) => sym('book', { ink: 'ink', ...o });

/** The answer's three slots. at: [t,t,t] each row arrives; ticks: [t|null x3]; done: [bool x3] ticked from the start; arrow: {i, at} puts "→" on row i. */
export function skeleton(o) {
  const id = o.id || uid('sk'), L = o.labels || ['पृष्ठभूमि', 'छह points', 'भारत की भूमिका'];
  const at = Array.isArray(o.at) ? o.at : [o.at, o.at, o.at];
  let h = '';
  L.forEach((lb, i) => {
    item(`${id}_r${i}`, { at: at[i], out: o.out, fx: at[i] === Math.min(...at) && !Array.isArray(o.at) ? 'fade' : 'slideL' });
    if (Array.isArray(o.at)) cue('slide', at[i]);
    const tk = (o.done || [])[i] ? at[i] : (o.ticks || [])[i];
    let extra = i === 1 ? `<span class="skp">${'<i></i>'.repeat(6)}</span>` : '';
    if (tk != null) { item(`${id}_k${i}`, { at: tk, out: o.out, fx: 'draw', len: 120, d: tk === at[i] ? 0 : .3 }); if (tk !== at[i]) cue('tick', tk); extra += `<svg class="skk" width="84" height="84" viewBox="0 0 100 100"><path id="${id}_k${i}" d="M12 54 L38 80 L88 20" fill="none" stroke="currentColor" stroke-width="13" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="120" stroke-dashoffset="120"/></svg>`; }
    if (o.arrow && o.arrow.i === i) { item(`${id}_a${i}`, { at: o.arrow.at, out: o.out, fx: 'slideL' }); extra += `<span id="${id}_a${i}" class="sub ska">${arrowGlyph(70)}</span>`; }
    h += `<div id="${id}_r${i}" class="sub skr"><b>${i + 1}</b><span class="skl">${lb}</span>${extra}</div>`;
  });
  item(id, { at: Math.min(...at), out: o.out, fx: 'none' });
  return `<div id="${id}" class="it sk" style="${pos({ w: 760, ...o })}">${h}</div>`;
}

/** A type-only name plate: small title over a big name, cream on a solid ink block. */
export const plate = o => el({ ...o, ink: o.ink || 'ink' }, 'pl', `${o.title ? `<div class="plt">${o.title}</div>` : ''}<div class="pln">${o.name}</div>`, { fx: 'slideL', cueKind: 'slide' });

/** Fill-in tiles with n-of-N. items: [{html, at, ink, sub}]; at = when the empty slots appear. cols, h (tile height), gap, size (font px), count (default true). */
export function tiles(o) {
  const id = o.id || uid('tl'), n = o.items.length, cols = o.cols || 1, gap = o.gap ?? 20, th = o.th || 124;
  let h = '';
  o.items.forEach((it, i) => {
    item(`${id}_${i}`, { at: it.at, out: o.out, fx: 'press' }); cue('slide', it.at);
    h += `<div class="tls" style="height:${th}px"><div id="${id}_${i}" class="sub tlf ${it.ink || 'ink'}" style="font-size:${o.size || 60}px">${it.html}${it.sub ? `<small>${it.sub}</small>` : ''}</div></div>`;
  });
  let cnt = '';
  if (o.count !== false) {
    o.items.forEach((it, i) => { const nx = o.items[i + 1]; item(`${id}_c${i}`, { at: it.at, out: nx ? nx.at : o.out, fx: 'none', hold: true }); cnt += `<span id="${id}_c${i}" class="sub">${i + 1} / ${n}</span>`; });
    cnt = `<div class="tlc">${cnt}</div>`;
  }
  item(id, { at: o.at, out: o.out, fx: 'fade' });
  return `<div id="${id}" class="it tl" style="${pos({ w: 900, ...o })}">${cnt}<div class="tlg" style="grid-template-columns:repeat(${cols},1fr);gap:${gap}px">${h}</div></div>`;
}

/** The exam line, in the serif. html, or parts: [{html, at}] that arrive on his words. label: small tag above it. */
export function card(o) {
  const id = o.id || uid('cd');
  let inner = o.html || '';
  (o.parts || []).forEach((p, i) => { item(`${id}_${i}`, { at: p.at, out: o.out, fx: 'fade' }); inner += `<span id="${id}_${i}" class="sub">${p.html}</span> `; });
  return el({ w: 900, ...o, id }, 'cd', `${o.label ? `<div class="cdl">${o.label}</div>` : ''}${inner}`, { fx: 'slideU', cueKind: 'slide' });
}

const arrowGlyph = (sz, sw = 9) => `<svg class="ag" width="${sz}" height="${Math.round(sz * .6)}" viewBox="0 0 100 60" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round"><path d="M6 30 H90 M66 8 L92 30 L66 52"/></svg>`;
/** An arrow. With x1,y1,x2,y2: drawn across the frame (draws on in 0.3 s). With only size: an inline "→" glyph (no timeline). */
export function arrow(o = {}) {
  if (o.x1 == null) return arrowGlyph(o.size || 60, o.sw);
  const id = o.id || uid('ar'), dx = o.x2 - o.x1, dy = o.y2 - o.y1, len = Math.hypot(dx, dy), a = Math.atan2(dy, dx), hw = o.head || 26, sw = o.sw || 9;
  const hx = (k, s) => (o.x2 - hw * Math.cos(a) + s * hw * .6 * Math.sin(a)).toFixed(1) + ' ' + (o.y2 - hw * Math.sin(a) - s * hw * .6 * Math.cos(a)).toFixed(1);
  item(`${id}_s`, { at: o.at, out: o.out, fx: 'draw', len: Math.ceil(len), d: o.d ?? .3 });
  item(`${id}_h`, { at: o.at + (o.d ?? .3) - .05, out: o.out, fx: 'fade', d: .08 });
  return `<svg class="arw ${o.ink || 'ink'}" width="1080" height="1920" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" ${o.dash ? `stroke-dasharray="${o.dash}"` : ''}>` +
    `<path id="${id}_s" class="svi" d="M${o.x1} ${o.y1} L${o.x2} ${o.y2}" ${o.dash ? '' : `stroke-dasharray="${Math.ceil(len)}" stroke-dashoffset="${Math.ceil(len)}"`}/>` +
    `<path id="${id}_h" class="svi" d="M${hx(0, 1)} L${o.x2} ${o.y2} L${hx(0, -1)}"/></svg>`;
}

/** A picture file on the timeline (kept out of the DOM hash: it is a CSS background). */
export function img(o) {
  const cls = uid('im'), ext = path.extname(o.file).slice(1).replace('jpg', 'jpeg');
  REG.css.push(`.${cls}{background:url(${dataURL(o.file, 'image/' + ext)}) 50% 50%/contain no-repeat}`);
  REG.preload = (REG.preload || []).concat(cls);
  return el({ ...o, cls: `${cls} ${o.cls || ''}` }, 'bx', '', { fx: o.fx || 'slideD' });
}

/** Frame pixel of a map anchor (assets/map.json: nepal, india, kathmandu, delhi), the map sitting in the picture window. */
export function mapPt(name) {
  const M = JSON.parse(fs.readFileSync(path.join(VIDEO, 'assets/map.json'), 'utf8'));
  if (!M.anchors[name]) throw new Error(`map has no anchor ${name} (${Object.keys(M.anchors).join(' ')})`);
  return { x: LOOK.window.x + M.anchors[name][0], y: LOOK.window.y + M.anchors[name][1] };
}
/** THE MAP (assets/map.png) in the picture window, in an ink frame. labels: {nepal: t, india: t} print नेपाल / भारत on paper plates at their anchors when he says them. */
export function map(o) {
  const id = o.id || uid('mp'), W = LOOK.window;
  let h = img({ file: path.join(VIDEO, 'assets/map.png'), at: o.at, out: o.out, x: W.x, y: W.y, w: W.w, h: W.h, fx: o.fx || 'slideR', id, style: `border:5px solid var(--ink);background-size:cover;${o.style || ''}` });
  cue('slide', o.at);
  for (const [k, lb] of [['nepal', 'नेपाल'], ['india', 'भारत']]) {
    const t = (o.labels || {})[k]; if (t == null) continue;
    const p = mapPt(k);
    h += el({ id: `${id}_${k}`, at: t, out: o.out, x: p.x, y: p.y, style: 'transform-origin:0 0;margin:-42px 0 0 -90px;width:180px;text-align:center' }, 'mpl', lb, { fx: 'press', cueKind: 'stamp' });
  }
  return h;
}

/** The page "goes red" / "goes blue": a flat tint of the paper and a coloured page edge, t0..t1. */
export function wash(ink, t0, t1, o = {}) { REG.wash.push({ ink, t0: r3(t0), t1: r3(t1), a: o.a ?? .12, edge: o.edge !== false }); }

// ------------------------------------------------------------ THE LINE ----
// u = how far along the years (0..1), h = who holds power (0 = राजा, 1 = लोकतंत्र). A sketch, not a scale.
const NODES = [
  { k: 'start', u: 0, h: .16 },
  { k: '1990', u: .13, h: .16, dot: 'blue', lab: [0, .95] },
  { k: 'peak', u: .23, h: .66 },
  { k: 'edge', u: .39, h: .66 },                       // peak..edge is the wobbly 1990s
  { k: '2002', u: .47, h: 0, dot: 'red', lab: [0, .95] },
  { k: 'floor', u: .58, h: 0 },
  { k: '2006', u: .68, h: .52, dot: 'blue', lab: [1.25, .45] },
  { k: 'sabha', u: .75, h: .76 },                      // संविधान-सभा, between 2006 and 2008 (part 2 marks it)
  { k: '2008', u: .82, h: 1, dot: 'blue', lab: [-.95, -.8] },
  { k: '2015', u: 1, h: 1, dot: 'blue', lab: [-.9, .95] },
];
const STOPS = [[0, 'red'], [.13, 'red'], [.2, 'blue'], [.39, 'blue'], [.47, 'red'], [.58, 'red'], [.66, 'blue'], [1, 'blue']];
const nodeU = k => { if (typeof k === 'number') return k; const n = NODES.find(n => n.k === String(k)); if (!n) throw new Error(`the line has no point "${k}" (${NODES.map(n => n.k).join(' ')})`); return n.u; };
/** Where the line sits. strip = the thin strip (y 60-250); full = the page (he is hidden or small); mid = y 280-800 above him when he is large. */
export const MODES = {
  strip: { x: 236, y: 112, w: 796, h: 84, yf: 42, row: 1, af: 40, tf: 40, sw: 7, r: 9, a: 1 },
  full: { x: 170, y: 560, w: 780, h: 520, yf: 92, row: 0, af: 56, tf: 84, sw: 16, r: 22, a: 1 },
  mid: { x: 190, y: 400, w: 760, h: 270, yf: 60, row: 0, af: 44, tf: 60, sw: 11, r: 15, a: 1 },
};
const L = () => REG.line || (REG.line = { nodes: NODES, stops: STOPS, trans: [], last: null, ink0: 0, pencil0: 0, ink: [], pencil: [], names: [], title: null, stop: [], wob: [], marks: [], glow: [], axis: true, inkNow: 0 });
const modeOf = m => { if (typeof m === 'string') { if (!MODES[m]) throw new Error(`no line mode ${m}`); return { ...MODES[m] }; } return { ...MODES.full, ...m }; };
export const line = {
  /** The state at t=0. ink / pencil: a point name or 0..1; named: years already numbered; mode: strip | full | mid | off. */
  start({ ink = 0, pencil = 0, named = [], title = false, mode = 'off', axis = true } = {}) {
    const l = L(); l.ink0 = l.inkNow = nodeU(ink); l.pencil0 = nodeU(pencil); l.axis = axis;
    named.forEach(k => l.names.push({ k: String(k), t: -1, on: 1 }));
    if (title) l.title = -1;
    if (mode !== 'off') { l.last = modeOf(mode); l.trans.push({ t: -1, from: l.last, to: l.last }); }
    return line;
  },
  /** From t (a cut), show the line as m: 'strip' | 'full' | 'mid' | 'off' | {x,y,w,h,...}. Glides 0.5 s centred on t. */
  mode(t, m) {
    const l = L(), to = m === 'off' ? { ...(l.last || MODES.strip), a: 0 } : modeOf(m);
    const from = l.last && l.last.a > 0 ? l.last : { ...to, a: 0 };
    l.trans.push({ t: r3(t), from, to }); l.last = to; return line;
  },
  /** Draw the pencilled route as far as `to` (a point name or 0..1), from t over d seconds. */
  pencil(to, t, d = 1.2) { L().pencil.push({ t: r3(t), d, to: nodeU(to) }); if (d > 0) cue('scratch', t, d); return line; },
  /** Ink the line as far as `to`, from t over d seconds. o.ease: io (default) | in | lin. o.drop: a heavy fall (cue 'drop'). */
  ink(to, t, d = 1, o = {}) { const l = L(); l.ink.push({ t: r3(t), d, to: nodeU(to), ease: o.ease || (o.drop ? 'in' : 'io') }); l.inkNow = nodeU(to); if (o.drop) cue('drop', t + d * .8); else if (d > 0 && o.cue !== false) cue('scratch', t, d); return line; },
  /** A year dot gets its number at t (only when he says the year). */
  name(k, t) { L().names.push({ k: String(k), t: r3(t), on: 1 }); cue('tick', t); return line; },
  /** "लोकतंत्र की राह" is printed on the line from t. */
  title(t) { L().title = r3(t); return line; },
  /** The red bar "रुक गई" across the line at its head, t0..t1. */
  stop(t0, t1, u) { const l = L(); l.stop.push({ t0: r3(t0), t1: r3(t1), u: u == null ? l.inkNow : nodeU(u) }); cue('stamp', t0); return line; },
  /** The 1990s stretch shakes, t0..t1. */
  wobble(t0, t1) { L().wob.push({ t0: r3(t0), t1: r3(t1) }); return line; },
  /** A small mark on the line at a point (e.g. 'sabha') from t, with an optional label. */
  mark(k, t, o = {}) { L().marks.push({ u: nodeU(k), t: r3(t), label: o.label || '', ink: o.ink || 'blue' }); cue('tick', t); return line; },
  /** Move the glowing "you are here" ring to a point at t (by default it rides the ink's head). */
  glow(k, t) { L().glow.push({ u: nodeU(k), t: r3(t) }); return line; },
  /** Wipe it back to an empty line (axes and name stay) at t. */
  clear(t) { const l = L(); l.ink.push({ t: r3(t), d: .3, to: 0, ease: 'io' }); l.pencil.push({ t: r3(t), d: .3, to: 0 }); NODES.forEach(n => n.dot && l.names.push({ k: n.k, t: r3(t), on: 0 })); l.inkNow = 0; return line; },
  /** Static pixel position of a point in a mode (no wobble): {x, y}. For placing your own drawings. */
  pt(k, mode = 'strip') {
    const u = nodeU(k), m = modeOf(mode); let i = 0; while (i < NODES.length - 2 && NODES[i + 1].u < u) i++;
    const a = NODES[i], b = NODES[i + 1], p = (u - a.u) / (b.u - a.u), h = a.h + (b.h - a.h) * p;
    return { x: +(m.x + u * m.w).toFixed(1), y: +(m.y + m.h * (1 - h)).toFixed(1) };
  },
  u: nodeU,
};
/** The line as the thin strip from t (same as line.mode(t,'strip')). */
export const strip = t => line.mode(t, 'strip');
/** The line full-page from t (same as line.mode(t,'full')). */
export const lineFull = t => line.mode(t, 'full');

// --------------------------------------------------------------- CSS ----
const fontFace = () => {
  const F = LOOK.fonts, u = f => dataURL(f, 'font/ttf');
  return `@font-face{font-family:Khand;font-weight:700;src:url(${u(F.head[0])}) format('truetype')}` +
    `@font-face{font-family:Khand;font-weight:600;src:url(${u(F.head[1])}) format('truetype')}` +
    `@font-face{font-family:Mukta;font-weight:800;src:url(${u(F.body[0])}) format('truetype')}` +
    `@font-face{font-family:Tiro;font-weight:400;src:url(${u(F.serif[0])}) format('truetype')}`;
};
const W = LOOK.window, C = LOOK.captions;
const baseCSS = () => `
:root{--paper:${LOOK.paper};--ink:${LOOK.ink};--red:${LOOK.red};--blue:${LOOK.blue};--slip:#fbf7ec}
html,body{margin:0;background:transparent}
#st{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mukta,sans-serif;color:var(--ink)}
.layer{position:absolute;inset:0;display:none}
.red{--c:var(--red)}.blue{--c:var(--blue)}.ink{--c:var(--ink)}
b.red,b.blue,b.ink,span.red,span.blue,span.ink,svg.red,svg.blue,svg.ink{color:var(--c)}
/* under: opaque paper, a hole at the picture window */
#L_under{--pg:var(--paper)}
#L_under>.pg,#sh{position:absolute;background:var(--pg)}
#hole{position:absolute;left:${W.x}px;top:${W.y}px;width:${W.w}px;height:${W.h}px;overflow:hidden}
#dots{position:absolute;inset:0;background-image:radial-gradient(circle,var(--paper) 1.2px,transparent 1.6px);background-size:7px 7px;opacity:.3}
#hfr{position:absolute;inset:0;border:5px solid var(--ink);box-sizing:border-box}
#sh{inset:0}
#edge{position:absolute;inset:0;border:16px solid var(--red);box-sizing:border-box;opacity:0}
#L_mask{background:#000}#mk{position:absolute;inset:0;background:#fff}
#pv_bg{background:var(--paper)}#pv_box{position:absolute;left:${W.x}px;top:${W.y}px;width:${W.w}px;height:${W.h}px;background:#8d8d8d}
#pv_pres{position:absolute;left:0;top:0;width:${LOOK.pcrop.w}px;height:${LOOK.pcrop.h}px;transform-origin:0 0;display:none;
  background:url(${dataURL(path.join(VIDEO, 'assets/presenter_cutout.png'), 'image/png')}) 0 0/100% 100% no-repeat;
  filter:drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(0 12px 14px rgba(0,0,0,.3))}
#pv_cap{position:absolute;left:40px;right:40px;top:${C.y0}px;height:${C.y1 - C.y0}px;border:3px dashed rgba(27,26,23,.35);box-sizing:border-box;display:none}
#ln,.arw{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;pointer-events:none}
.arw{color:var(--c)}.svi{opacity:0;visibility:hidden}
/* timeline items */
.it{position:absolute;opacity:0;visibility:hidden;box-sizing:border-box}
.sub{display:inline-block;opacity:0;visibility:hidden}
.tx{color:var(--c)}
.sy{display:block;color:var(--c)}
/* heading */
.hd .sub{transform-origin:50% 60%}
.hdr{display:flex;align-items:center;gap:30px}
.hdn{font:700 124px/1 Khand,Mukta;color:var(--paper);background:var(--c);min-width:150px;height:164px;padding:14px 18px 0;box-sizing:border-box;text-align:center}
.hdy{font:700 196px/1 Khand,Mukta;color:var(--c);padding-top:14px}
.hdt{font:700 112px/1.14 Khand,Mukta;color:var(--c);display:block;margin-top:4px}
.hd.band{display:flex;align-items:center;gap:22px;white-space:nowrap}
.hd.band .hdn{font-size:72px;min-width:86px;height:96px;padding:8px 12px 0}
.hd.band .hdy{font-size:96px;padding-top:8px}
.hd.band .hdt{font-size:80px;margin:0;padding-top:6px;display:inline-block}
/* slip */
.sl{background:var(--slip);border:2.5px solid var(--ink);box-shadow:7px 7px 0 rgba(27,26,23,.2);padding:12px 28px 8px;font:800 44px/1.3 Mukta;color:var(--ink);white-space:nowrap}
.sl .pin{position:absolute;left:50%;top:-11px;width:20px;height:20px;margin-left:-10px;border-radius:50%;background:var(--ink);box-shadow:2px 3px 0 rgba(27,26,23,.25)}
.sl b{font-weight:800}
/* stamp */
.sp{border:7px solid var(--c);outline:3px solid var(--c);outline-offset:5px;border-radius:12px;padding:6px 30px 0;font:700 84px/1.18 Khand,Mukta;color:var(--c);white-space:nowrap;letter-spacing:.01em}
/* pips */
.pp{display:flex}
.pip{position:relative;display:block;box-sizing:border-box;border:3px solid var(--ink);border-radius:50%}
.pipf{position:absolute;inset:-3px;border-radius:50%;background:var(--c);opacity:0;visibility:hidden}
/* skeleton */
.sk .skr{display:flex;align-items:center;gap:24px;height:124px;margin-bottom:22px;padding:6px 26px 0 0;box-sizing:border-box;background:var(--slip);border:4px solid var(--ink);font:700 76px/1 Khand,Mukta;white-space:nowrap}
.skr>b{flex:none;align-self:stretch;width:96px;margin-top:-6px;padding-top:6px;display:flex;align-items:center;justify-content:center;background:var(--ink);color:var(--paper);font:700 76px/1 Khand}
.skl{flex:1}
.skp{display:flex;gap:9px;margin-right:6px}.skp i{width:24px;height:24px;box-sizing:border-box;border:3px solid var(--ink);border-radius:50%}
.skk{flex:none;margin-top:-6px}.ska{flex:none;display:flex!important;align-items:center;margin-top:-6px}
/* plate */
.pl{background:var(--c);color:var(--paper);padding:12px 36px 6px;box-shadow:8px 8px 0 rgba(27,26,23,.2);white-space:nowrap}
.plt{font:800 40px/1.25 Mukta;opacity:.92}.pln{font:700 96px/1.15 Khand,Mukta}
/* tiles */
.tlg{display:grid}
.tls{position:relative;box-sizing:border-box;border:4px dashed rgba(27,26,23,.4)}
.tlf{position:absolute;inset:-4px;display:flex!important;flex-direction:column;align-items:center;justify-content:center;background:var(--c);color:var(--paper);font:700 60px/1.12 Khand,Mukta;text-align:center;padding-top:6px;box-sizing:border-box}
.tlf small{font:800 40px/1.2 Mukta;opacity:.92}
.tlc{position:relative;height:60px;margin-bottom:12px;font:700 52px/60px Khand}.tlc .sub{position:absolute;left:0;top:0}
/* exam-line card */
.cd{background:var(--slip);border:2.5px solid var(--ink);border-left-width:16px;box-shadow:8px 8px 0 rgba(27,26,23,.2);padding:22px 34px 20px;font:400 60px/1.45 Tiro,Mukta;color:var(--ink)}
.cdl{font:700 44px/1.2 Khand;margin-bottom:8px;letter-spacing:.02em}
.ag{display:inline-block;vertical-align:middle}
.mpl{background:var(--paper);border:3px solid var(--ink);font:700 64px/78px Khand,Mukta;color:var(--ink);padding-top:4px;height:84px}
`;

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
  const COL = { paper: D.look.paper, ink: D.look.ink, red: D.look.red, blue: D.look.blue };
  const SC = D.scenes, OUTD = .2;
  const sceneAt = t => { let i = 0; while (i < SC.length - 1 && t >= SC[i].t1) i++; return i; };
  /** env(t,a,b,din,dout): 0 outside a..b, eased 0→1 after a and 1→0 before b */
  const env = (t, a, b, din = .2, dout = .2) => t < a || (b != null && t >= b) ? 0 : Math.min(P(t, a, a + din), b == null ? 1 : 1 - P(t, b - dout, b));

  // ---- timeline items
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
        case 'slideL': o = clamp(p * 2.5); tf = 'translateX(' + f1(-90 * (1 - eout(p))) + 'px)'; break;
        case 'slideR': o = clamp(p * 2.5); tf = 'translateX(' + f1(90 * (1 - eout(p))) + 'px)'; break;
        case 'slideU': o = clamp(p * 2.5); tf = 'translateY(' + f1(70 * (1 - eout(p))) + 'px)'; break;
        case 'slideD': o = clamp(p * 2.5); tf = 'translateY(' + f1(-70 * (1 - eout(p))) + 'px)'; break;
        case 'pop': o = clamp(p * 3); tf = 'scale(' + f3(.4 + .6 * eback(p)) + ')'; break;
        case 'wipe': e.style.clipPath = p >= 1 ? 'none' : 'inset(0 ' + f1(100 * (1 - eout(p))) + '% 0 0)'; break;
        case 'draw': e.style.strokeDashoffset = f1(it.len * (1 - eout(p))); break;
      }
      e.style.visibility = 'visible'; e.style.opacity = f3(o * q);
      if (tf || it.rot) e.style.transform = tf + (it.rot ? ' rotate(' + it.rot + 'deg)' : '');
    }
  }

  // ---- presenter: visibility (mask) and place (preview)
  const PL = D.look.place;
  const seen = i => SC[i].presenter === 'hidden' ? 0 : 1;
  const placeOf = i => { for (const j of [i, i + 1, i - 1, i + 2, i - 2]) if (SC[j] && SC[j].presenter !== 'hidden') return PL[SC[j].presenter]; return PL.you; };
  function pres(t) {
    const i = sceneAt(t), s = SC[i], g = D.look.glide / 2, m = .125;
    let v = seen(i), a = placeOf(i), b = a, p = 0;
    if (i > 0 && t - s.t0 < g) { b = a; a = placeOf(i - 1); p = eio(.5 + (t - s.t0) / (2 * g)); }
    else if (i < SC.length - 1 && s.t1 - t < g) { b = placeOf(i + 1); p = eio(.5 - (s.t1 - t) / (2 * g)); }
    if (i > 0 && t - s.t0 < m) v = lerp(seen(i - 1), v, .5 + (t - s.t0) / (2 * m));
    else if (i < SC.length - 1 && s.t1 - t < m) v = lerp(v, seen(i + 1), .5 - (s.t1 - t) / (2 * m));
    return { v, s: lerp(a.s, b.s, p), x: lerp(a.x0, b.x0, p), y: lerp(a.y0, b.y0, p), state: s.presenter, scene: s };
  }

  // ---- under: paper, the hole and its shutter, the wash
  function drawUnder(t) {
    let o = 0, ink = 'ink';
    for (const s of SC) {
      if (!s.shots.length) continue;
      const a = s.shots[0].t0, b = s.shots[s.shots.length - 1].t1, v = eout(P(t, a, a + .35)) * (1 - ein(P(t, b - .35, b)));
      if (v > o) { o = v; ink = (s.shots.find(x => t < x.t1) || s.shots[s.shots.length - 1]).ink; }
    }
    $('sh').style.transform = 'translateX(' + f2(-100 * o) + '%)';
    $('hfr').style.borderColor = COL[ink];
    let wa = 0, wc = COL.red, we = 0;
    for (const w of D.wash) { const e = env(t, w.t0, w.t1, .4, .4); if (e * w.a > wa) { wa = e * w.a; wc = COL[w.ink]; we = w.edge ? e : 0; } }
    // red ink at 12% on cream is a clear pink; blue ink at 12% is GREY (cream is its complement), so
    // the blue page is its own pale blue, reached in full
    const bluePg = wc === COL.blue;
    $('L_under').style.setProperty('--pg', wa > 0 ? (bluePg ? mix(COL.paper, '#d7e4f7', Math.min(1, wa / .12)) : mix(COL.paper, wc, wa)) : COL.paper);
    $('edge').style.borderColor = wc; $('edge').style.opacity = f3(we);
  }

  // ---- THE LINE: one geometry for the strip and the full page
  const LN = D.line, NODES = LN ? LN.nodes : [];
  const SAMP = [];
  if (LN) {
    for (let i = 0; i < NODES.length - 1; i++) {
      const a = NODES[i], b = NODES[i + 1], n = a.k === 'peak' ? 8 : 5;
      for (let j = 0; j < n; j++) SAMP.push({ u: lerp(a.u, b.u, j / n), h: lerp(a.h, b.h, j / n), wob: a.k === 'peak' && j > 0 ? (j % 2 ? 1 : -1) : 0 });
    }
    const z = NODES[NODES.length - 1]; SAMP.push({ u: z.u, h: z.h, wob: 0 });
  }
  const colAt = u => { const S = LN.stops; let i = 0; while (i < S.length - 2 && S[i + 1][0] <= u) i++; const a = S[i], b = S[i + 1]; return a[1] === b[1] ? COL[a[1]] : mix(COL[a[1]], COL[b[1]], Math.round(clamp((u - a[0]) / (b[0] - a[0])) * 5) / 5); };
  const track = (keys, v0, t) => { let v = v0; for (const k of keys) { if (t < k.t) break; const p = k.d > 0 ? clamp((t - k.t) / k.d) : 1; v = lerp(v, k.to, k.ease === 'in' ? p * p : k.ease === 'lin' ? p : eio(p)); if (p < 1) break; } return v; };
  const KEYS = ['x', 'y', 'w', 'h', 'yf', 'row', 'af', 'tf', 'sw', 'r', 'a'];
  function modeAt(t) {
    const T = LN.trans; let i = -1;
    for (let j = 0; j < T.length; j++) if (t >= T[j].t - .25) i = j;
    if (i < 0) return null;
    const tr = T[i], p = tr.t < 0 ? 1 : eio(P(t, tr.t - .25, tr.t + .25)), m = {};
    for (const k of KEYS) m[k] = lerp(tr.from[k], tr.to[k], p);
    return m;
  }
  const named = (k, t) => { let v = 0; for (const e of LN.names) if (e.k === k && e.t <= t) v = e.on ? P(t, e.t, e.t + .2) : 0; return v; };
  function linePts(m, t) {
    const tq = Math.floor(t * 8 + 1e-6) / 8;      // the shake is drawn on eights of a second: fewer frames, and it looks hand-made
    let W = 0; for (const w of LN.wob) W = Math.max(W, env(tq, w.t0, w.t1, .3, .3));
    return SAMP.map((s, i) => ({ u: s.u, x: m.x + s.u * m.w, y: m.y + m.h * (1 - (s.h + s.wob * (.035 + W * .075 * Math.sin(tq * 23 + i * 2.1)))) }));
  }
  const ptAt = (pts, u) => { let i = 0; while (i < pts.length - 2 && pts[i + 1].u < u) i++; const a = pts[i], b = pts[i + 1], p = clamp((u - a.u) / (b.u - a.u)); return { u, x: lerp(a.x, b.x, p), y: lerp(a.y, b.y, p) }; };
  const cut = (pts, u0, u1) => { const o = [ptAt(pts, u0)]; for (const p of pts) if (p.u > u0 + 1e-9 && p.u < u1 - 1e-9) o.push(p); o.push(ptAt(pts, u1)); return o; };
  const dOf = a => a.map((p, i) => (i ? 'L' : 'M') + f1(p.x) + ' ' + f1(p.y)).join('');
  const TXT = (x, y, size, fill, s, o = {}) => '<text x="' + f1(x) + '" y="' + f1(y) + '" font-family="Khand,Mukta" font-weight="' + (o.w || 700) + '" font-size="' + f1(size) + '" fill="' + fill + '" text-anchor="' + (o.anchor || 'middle') +
    '" dominant-baseline="central" opacity="' + f3(o.o == null ? 1 : o.o) + '" stroke="' + COL.paper + '" stroke-width="' + f1(size * .16) + '" stroke-linejoin="round" paint-order="stroke">' + s + '</text>';
  /** Pixel position of a point of the line at time t (null while the line is off). */
  function linePoint(u, t) { const m = LN && modeAt(t); return m ? ptAt(linePts(m, t), u) : null; }
  function drawLine(t) {
    const g = $('lnG'); if (!LN) return;
    const m = modeAt(t);
    if (!m || m.a < .004) { if (g.innerHTML) g.innerHTML = ''; return; }
    const td = Math.floor(t * 15 + 1e-6) / 15;     // the line is DRAWN at 15 steps a second: half the frames to store
    const ink = track(LN.ink, LN.ink0, td), pen = track(LN.pencil, LN.pencil0, td), pts = linePts(m, t);
    let s = '';
    // axis: who holds power
    if (LN.axis) {
      const ax = m.x - lerp(34, 12, m.row), y0 = m.y - m.r, y1 = m.y + m.h + m.r, aw = Math.max(2.5, m.sw * .28), ao = Math.abs(2 * m.row - 1);
      s += '<path d="M' + f1(ax) + ' ' + f1(y1) + 'V' + f1(y0) + '" stroke="' + COL.ink + '" stroke-width="' + f1(aw) + '" opacity=".55"/>' +
        '<path d="M' + f1(ax - aw * 2.4) + ' ' + f1(y0 + aw * 3) + 'L' + f1(ax) + ' ' + f1(y0 - aw * 1.5) + 'L' + f1(ax + aw * 2.4) + ' ' + f1(y0 + aw * 3) + 'Z" fill="' + COL.ink + '" opacity=".55"/>';
      if (m.row > .5) s += TXT(ax - 10, m.y + 4, m.af, COL.blue, 'लोकतंत्र', { anchor: 'end', w: 600, o: ao }) + TXT(ax - 10, m.y + m.h, m.af, COL.red, 'राजा का शासन', { anchor: 'end', w: 600, o: ao });
      else s += TXT(ax - 40, m.y - m.af * 1.25, m.af, COL.blue, 'लोकतंत्र', { anchor: 'start', w: 600, o: ao }) + TXT(ax - 40, m.y + m.h + m.af * 2.2, m.af, COL.red, 'राजा का शासन', { anchor: 'start', w: 600, o: ao });
    }
    // the pencilled route
    if (pen > .001) s += '<path d="' + dOf(cut(pts, 0, pen)) + '" fill="none" stroke="' + COL.ink + '" stroke-width="' + f1(Math.max(3, m.sw * .42)) + '" stroke-linecap="round" stroke-dasharray="0.1 ' + f1(Math.max(9, m.sw * 1.25)) + '" opacity=".5"/>';
    // the inked line, piece by piece in the ink of whoever holds power there
    if (ink > .001) for (let i = 0; i < pts.length - 1 && pts[i].u < ink; i++) {
      const b = pts[i + 1].u <= ink ? pts[i + 1] : ptAt(pts, ink);
      s += '<path d="M' + f1(pts[i].x) + ' ' + f1(pts[i].y) + 'L' + f1(b.x) + ' ' + f1(b.y) + '" stroke="' + colAt((pts[i].u + pts[i + 1].u) / 2) + '" stroke-width="' + f1(m.sw) + '" stroke-linecap="round"/>';
    }
    // marks
    for (const k of LN.marks) { const o = P(t, k.t, k.t + .2); if (o <= 0) continue; const p = ptAt(pts, k.u), r = m.r * .95;
      s += '<path d="M' + f1(p.x) + ' ' + f1(p.y - r) + 'L' + f1(p.x + r) + ' ' + f1(p.y) + 'L' + f1(p.x) + ' ' + f1(p.y + r) + 'L' + f1(p.x - r) + ' ' + f1(p.y) + 'Z" fill="' + COL[k.ink] + '" stroke="' + COL.paper + '" stroke-width="' + f1(m.r * .3) + '" opacity="' + f3(o) + '"/>';
      if (k.label) s += TXT(p.x - m.r * 1.6, p.y - m.r * .6, Math.max(40, m.yf * .7), COL[k.ink], k.label, { anchor: 'end', o }); }
    // the ring on "you are here"
    let hu = ink > .001 ? ink : -1; for (const e of LN.glow) if (e.t <= t) hu = e.u;
    if (hu >= 0) { const p = ptAt(pts, hu), c = colAt(hu); s += '<circle cx="' + f1(p.x) + '" cy="' + f1(p.y) + '" r="' + f1(m.r * 2.1) + '" fill="' + c + '" opacity=".2"/><circle cx="' + f1(p.x) + '" cy="' + f1(p.y) + '" r="' + f1(m.r * 2.1) + '" fill="none" stroke="' + c + '" stroke-width="' + f1(Math.max(2, m.r * .22)) + '" opacity=".75"/>'; }
    // the year dots and their numbers
    for (const n of NODES) {
      if (!n.dot) continue;
      const got = ink >= n.u - .002, p = ptAt(pts, n.u);
      if (got) s += '<circle cx="' + f1(p.x) + '" cy="' + f1(p.y) + '" r="' + f1(m.r) + '" fill="' + COL[n.dot] + '" stroke="' + COL.paper + '" stroke-width="' + f1(m.r * .3) + '"/>';
      else if (pen >= n.u - .002) s += '<circle cx="' + f1(p.x) + '" cy="' + f1(p.y) + '" r="' + f1(m.r * .82) + '" fill="' + COL.paper + '" stroke="' + COL.ink + '" stroke-width="' + f1(Math.max(2.5, m.r * .3)) + '"/>';
      const o = named(n.k, t);
      if (o > 0) s += TXT(lerp(p.x + n.lab[0] * m.yf, p.x, m.row), lerp(p.y + (n.lab[1] > 0 ? m.r : -m.r) + n.lab[1] * m.yf, m.y + m.h + 34, m.row), m.yf, got ? COL[n.dot] : COL.ink, n.k, { o });
    }
    // रुक गई
    for (const b of LN.stop) { const e = env(t, b.t0, b.t1, .12, .15); if (e <= 0) continue; const p = ptAt(pts, b.u), bw = m.sw * 1.2, bh = m.r * 6 * (b.t1 - t < .15 ? 1 : eout(P(t, b.t0, b.t0 + .12))), fs = Math.max(40, m.yf * .95);
      s += '<rect x="' + f1(p.x + m.r * 1.3) + '" y="' + f1(p.y - bh / 2) + '" width="' + f1(bw) + '" height="' + f1(bh) + '" fill="' + COL.red + '" opacity="' + f3(e) + '"/>' +
        TXT(p.x + m.r * 1.3 + bw + fs * .22, p.y - fs * .78, fs, COL.red, 'रुक गई', { anchor: 'start', o: e }); }
    // its name
    if (LN.title != null && t >= LN.title) s += TXT(m.x + m.w * lerp(.5, .53, m.row), m.y - lerp(m.tf * 2.5, 32, m.row), m.tf, COL.ink, 'लोकतंत्र की राह', { o: P(t, LN.title, LN.title + .3) });
    g.innerHTML = s; g.setAttribute('opacity', f3(m.a));
  }

  function hash(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193); } return (h >>> 0).toString(36) + ':' + s.length; }
  const SHOW = { under: ['L_under'], mask: ['L_mask'], overlay: ['L_overlay'], preview: ['pv_bg', 'L_under', 'pv_pres', 'L_overlay', 'pv_cap'] };
  const ALL = ['pv_bg', 'L_under', 'L_mask', 'pv_pres', 'L_overlay', 'pv_cap'];
  window.frameKey = layer => hash((SHOW[layer] || []).map(id => $(id).outerHTML).join(''));
  window.render = (t, layer) => {
    const show = SHOW[layer] || [];
    for (const id of ALL) $(id).style.display = show.includes(id) ? 'block' : 'none';
    if (layer === 'under' || layer === 'preview') { drawUnder(t); if (window.frameUnder) window.frameUnder(t); }
    if (layer === 'mask') $('mk').style.opacity = f3(pres(t).v);
    if (layer === 'overlay' || layer === 'preview') { runItems(t); drawLine(t); if (window.frame) window.frame(t); }
    if (layer === 'preview') { const p = pres(t); $('pv_pres').style.opacity = f3(p.v); $('pv_pres').style.transform = 'translate(' + f1(p.x) + 'px,' + f1(p.y) + 'px) scale(' + f3(p.s) + ')'; }
  };
  const pre = (D.preload || []).map(c => { const u = /url\(([^)]+)\)/.exec([...document.styleSheets[0].cssRules].find(r => r.selectorText === '.' + c).style.backgroundImage.replace(/"/g, '')); const im = new Image(); im.src = u[1]; return im.decode().catch(() => { }); });
  window.READY = Promise.all([...pre, ...['700 40px Khand', '600 40px Khand', '800 40px Mukta', '400 40px Tiro'].map(f => document.fonts.load(f, 'कख 12 ab'))]);
  Object.assign(window, { $, clamp, P, eout, ein, eio, eback, lerp, f1, f2, f3, mix, COL, SC, env, sceneAt, pres, linePoint, D });
}

/** Wrap your own browser code: browser(function (T) { window.frame = t => {...} }, data). Helpers in scope there: $, clamp, P, env, eout, ein, eio, eback, lerp, f1 f2 f3, mix, COL, SC, sceneAt, linePoint(u,t). */
export const browser = (fn, data = {}) => `;(${fn.toString()})(${JSON.stringify(data)});`;

/** The page. html = your overlay elements; css = your extra CSS; js = browser(...) code that may set window.frame(t) / window.frameUnder(t). */
export function stage({ css = '', html = '', js = '', part }) {
  if (!REG.spec || (part && part !== REG.part)) load(part);
  const D = {
    look: { paper: LOOK.paper, ink: LOOK.ink, red: LOOK.red, blue: LOOK.blue, place: LOOK.place, glide: LOOK.glide },
    scenes: REG.spec.scenes.map(s => ({ id: s.id, t0: s.t0, t1: s.t1, presenter: s.presenter, shots: s.shots.map(x => ({ t0: x.t0, t1: x.t1, ink: x.ink })) })),
    items: REG.items, wash: REG.wash, line: REG.line, preload: REG.preload || [],
  };
  const b = y => `<div class="pg" style="${y}"></div>`;
  return `<!doctype html><html><head><meta charset="utf-8"><style>${fontFace()}${baseCSS()}${REG.css.join('')}${css}</style></head><body>
<div id="st">
 <div id="pv_bg" class="layer"><div id="pv_box"></div></div>
 <div id="L_under" class="layer">${b(`left:0;top:0;width:1080px;height:${W.y}px`)}${b(`left:0;top:${W.y + W.h}px;width:1080px;height:${1920 - W.y - W.h}px`)}${b(`left:0;top:${W.y}px;width:${W.x}px;height:${W.h}px`)}${b(`left:${W.x + W.w}px;top:${W.y}px;width:${1080 - W.x - W.w}px;height:${W.h}px`)}
  <div id="hole"><div id="dots"></div><div id="hfr"></div><div id="sh"></div></div><div id="edge"></div></div>
 <div id="L_mask" class="layer"><div id="mk"></div></div>
 <div id="pv_pres"></div>
 <div id="L_overlay" class="layer"><svg id="ln" viewBox="0 0 1080 1920" fill="none"><g id="lnG"></g></svg>${html}</div>
 <div id="pv_cap"></div>
</div>
<script>(${ENGINE.toString()})(${JSON.stringify(D)});${js}</script></body></html>`;
}

// ---------------------------------------------------------------- cli ----
const zoomed = (html, z) => html.replace('</style>', `html{zoom:${z}}</style>`);
/** node partN.mjs [--workers n] | --stills t1,t2 [--layer preview] [--full] | --cues | --sheet */
export async function cli({ html, part, dur }) {
  const a = process.argv.slice(2), out = path.join(VIDEO, 'out'), opt = k => { const i = a.indexOf(k); return i < 0 ? null : a[i + 1]; };
  if (a.includes('--cues')) {
    const seen = new Set(), list = REG.cues.slice().sort((x, y) => x.t - y.t || x.kind.localeCompare(y.kind)).filter(c => { const k = c.kind + ':' + c.t.toFixed(2); if (seen.has(k) || c.t >= dur) return false; seen.add(k); return true; });
    const f = path.join(out, `cues_p${part}.json`);
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
  const stats = await renderLayers({ html, outDir: path.join(out, `layers/p${part}`), dur, layers: ['under', 'mask', 'overlay'], workers: +(opt('--workers') || 3) });
  console.log(JSON.stringify(stats));
}
