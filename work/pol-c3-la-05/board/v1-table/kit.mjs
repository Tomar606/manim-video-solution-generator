// POL-C3-LA-05 "गोल मेज़" (the round table): the ONE definition of the look. part1/2.mjs import this.
// This file may only DRAW. Timing comes from tools/reel/words.mjs (through the stage),
// the timeline engine and the layer renderer from tools/reel/.
//
// The picture is a walnut table seen from above. Its round leather disc is the window
// the Veo clips play in (the hole is cut in the under layer, so a clip is round);
// eight brass seat plates sit round the ring once the countries "sit together";
// a strip at the top holds परिचय · the five point cards · निष्कर्ष as they are laid.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createStage, dataURL } from '../../../tools/reel/components/stage.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const VIDEO = path.resolve(HERE, '..');
const K = createStage({ video: VIDEO, slug: 'pol-c3-la-05' });
export const { LOOK, item, cue, uid } = K;
const r3 = x => +(+x).toFixed(3);
const A = f => path.join(VIDEO, 'assets', f);

// ------------------------------------------------------------ time ----
export function load(part) {
  const L = K.load(part);
  /** onset of the first word at or after `from` that starts with `prefix` */
  L.atw = (prefix, from = 0) => { const w = L.K.words.find(w => w.s >= from - .02 && w.w.startsWith(prefix)); if (!w) throw new Error(`no word starting "${prefix}" after ${from}`); return +w.s.toFixed(3); };
  return L;
}

// ------------------------------------------------------- the table ----
// What the under layer draws, registered from the part files.
const TBL = { seats: null, turns: [], cracks: [], glow: [], mapDisc: [], mapFull: [] };
export const table = {
  /** The eight plates: scattered on the disc from `from` (with storm clouds over them), seated round the ring over [t0, t1]. Without from: seated already at t0. */
  seat(t0, t1 = t0, from = null) { TBL.seats = { t0: r3(t0), t1: r3(t1), from: from == null ? null : r3(from) }; if (t1 > t0) cue('slide', t0, t1 - t0); },
  /** A quarter-turn of the table (the plates move round one place). */
  turn(t) { TBL.turns.push(r3(t)); cue('turn', t, .7); },
  /** A coral crack across the disc. i = 0..2 picks its course. */
  crack(i, t) { TBL.cracks.push({ i, t: r3(t), out: null }); cue('crack', t); },
  /** Every crack still open fades out from t (the table holds). */
  heal(t) { for (const c of TBL.cracks) if (c.out == null) c.out = r3(t); },
  /** The brass ring lights all the way round from t. */
  glow(t, out = null) { TBL.glow.push({ t: r3(t), out: out == null ? null : r3(out) }); cue('chime', t); },
  /** The inlaid map inside the disc, t0..t1. */
  mapDisc(t0, t1) { TBL.mapDisc.push([r3(t0), r3(t1)]); cue('iris', t0); },
  /** The inlaid map over the whole frame, t0..t1. */
  mapFull(t0, t1) { TBL.mapFull.push([r3(t0), r3(t1)]); cue('slide', t0); },
};
export const SCATTER = [[-.6, -.5], [.08, -.7], [.62, -.4], [-.72, .08], [.66, .24], [-.42, .58], [.24, .64], [-.05, .02]];
/** Frame position of seat i (0 = top, clockwise) for a presenter state, before any turn. */
export function seatPt(i, state = 'explain', ext = 44) {
  const d = LOOK.disc[state], a = -Math.PI / 2 + i * Math.PI / 4 + Math.PI / 8;
  return { x: d.cx + (d.r + ext) * Math.cos(a), y: d.cy + (d.r + ext) * Math.sin(a), a };
}
export const disc = state => LOOK.disc[state];

// ------------------------------------------------------- the strip ----
// परिचय · 1 2 3 4 5 · निष्कर्ष across the top. at: when the strip comes in; fill: when each slot gets its card.
const STRIP = { on: false };
const ICON = {
  table: `<ellipse cx="50" cy="66" rx="30" ry="14" fill="currentColor"/><circle cx="16" cy="38" r="11" fill="currentColor"/><path d="M4 74 V58 Q4 50 16 50 Q28 50 28 58 V66 Z" fill="currentColor"/><circle cx="84" cy="38" r="11" fill="currentColor"/><path d="M96 74 V58 Q96 50 84 50 Q72 50 72 58 V66 Z" fill="currentColor"/><circle cx="50" cy="24" r="11" fill="currentColor"/><path d="M38 52 V44 Q38 36 50 36 Q62 36 62 44 V52 Z" fill="currentColor"/>`,
  bowl: `<path d="M12 50 H88 Q86 82 50 86 Q14 82 12 50 Z" fill="currentColor"/><path d="M24 48 Q30 26 50 24 Q70 26 76 48 Z" fill="currentColor" opacity=".55"/><rect x="34" y="86" width="32" height="7" rx="3" fill="currentColor"/>`,
  truck: `<rect x="6" y="30" width="54" height="38" rx="4" fill="currentColor"/><path d="M60 42 H80 L94 56 V68 H60 Z" fill="currentColor"/><circle cx="24" cy="74" r="10" fill="currentColor"/><circle cx="78" cy="74" r="10" fill="currentColor"/><circle cx="24" cy="74" r="4" fill="var(--bg,#f6eedc)"/><circle cx="78" cy="74" r="4" fill="var(--bg,#f6eedc)"/>`,
  book: `<path d="M50 26 C38 15 20 15 6 21 V84 C20 78 38 78 50 89 C62 78 80 78 94 84 V21 C80 15 62 15 50 26 Z" fill="currentColor"/><path d="M50 28 V86" stroke="var(--bg,#f6eedc)" stroke-width="4"/>`,
  crack: `<circle cx="50" cy="50" r="38" fill="none" stroke="currentColor" stroke-width="10"/><path d="M50 8 L42 36 L58 50 L44 66 L52 92" fill="none" stroke="currentColor" stroke-width="9" stroke-linejoin="round"/>`,
  steth: `<path d="M26 12 V40 Q26 62 46 62 Q66 62 66 40 V12" fill="none" stroke="currentColor" stroke-width="9" stroke-linecap="round"/><path d="M46 62 V74 Q46 88 62 88 Q76 88 76 74 V66" fill="none" stroke="currentColor" stroke-width="8"/><circle cx="76" cy="60" r="10" fill="currentColor"/>`,
  flask: `<path d="M38 10 H62 M42 10 V40 L16 84 Q14 92 24 92 H76 Q86 92 84 84 L58 40 V10" fill="none" stroke="currentColor" stroke-width="8" stroke-linejoin="round"/><path d="M27 70 H73 L82 86 H18 Z" fill="currentColor"/>`,
  gear: `<g fill="currentColor">${[0, 1, 2, 3, 4, 5, 6, 7].map(i => `<rect x="43" y="4" width="14" height="20" rx="3" transform="rotate(${i * 45} 50 50)"/>`).join('')}<circle cx="50" cy="50" r="30"/></g><circle cx="50" cy="50" r="12" fill="var(--bg,#f6eedc)"/>`,
  cloud: `<path d="M24 70 Q8 70 8 56 Q8 42 24 42 Q28 24 46 24 Q62 24 68 38 Q90 36 92 54 Q92 70 74 70 Z" fill="currentColor"/><path d="M40 74 L32 92 M56 74 L48 92 M72 74 L64 92" stroke="currentColor" stroke-width="5" stroke-linecap="round"/>`,
  tick: `<path d="M12 54 L38 80 L88 20" fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>`,
  cross: `<path d="M18 18 L82 82 M82 18 L18 82" fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="round"/>`,
  up: `<path d="M50 90 V16 M20 44 L50 12 L80 44" fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>`,
  person: `<circle cx="50" cy="24" r="16" fill="currentColor"/><path d="M20 96 V66 Q20 44 50 44 Q80 44 80 66 V96 Z" fill="currentColor"/>`,
  crate: `<rect x="10" y="22" width="80" height="62" rx="4" fill="currentColor"/><path d="M10 22 L90 84 M90 22 L10 84" stroke="var(--bg,#f6eedc)" stroke-width="6"/>`,
};
export const POINT_ICON = ['table', 'bowl', 'truck', 'book', 'crack'];
/** Inline SVG icon (no timeline). */
export function icon(name, size = 80, color = 'currentColor', style = '') {
  if (!ICON[name]) throw new Error(`no icon ${name}`);
  return `<svg width="${size}" height="${size}" viewBox="0 0 100 100" style="color:${color};${style}">${ICON[name]}</svg>`;
}
/** The strip. at: it comes in; intro: परिचय tag time; fill: [t|null x5]; filled: how many are full at `at`; end: निष्कर्ष time or null; ticks: [t parichay, t points, t nishkarsh] for the payoff. now: [[t, 'p'|0..4|'n'], ...] which slot glows from when. */
export function strip(o) {
  STRIP.on = true; STRIP.now = (o.now || []).map(([t, k]) => [r3(t), k]);
  const id = 'strip', fill = o.fill || [];
  let h = '';
  const slot = (k, inner, w, t, ticks) => {
    let f = '';
    if (t != null) { item(`${id}_f${k}`, { at: t, out: null, fx: t <= o.at ? 'none' : 'drop' }); if (t > o.at) { cue('knock', t); } f = `<div id="${id}_f${k}" class="sub sf">${inner}</div>`; }
    let tk = '';
    if (ticks != null) { item(`${id}_k${k}`, { at: ticks, out: null, fx: 'pop' }); cue('tick', ticks); tk = `<i id="${id}_k${k}" class="sub stk">${icon('tick', 40, '#2f7d6d')}</i>`; }
    return `<div class="ss" id="${id}_s${k}" style="width:${w}px">${f}${tk}</div>`;
  };
  const T = o.ticks || [];
  h += slot('p', '<b class="sw">परिचय</b>', 176, o.intro ?? o.at, T[0]);
  for (let i = 0; i < 5; i++) {
    const t = i < (o.filled || 0) ? o.at : fill[i];
    h += slot(i, `<b class="sn">${i + 1}</b>${icon(POINT_ICON[i], 50, i === 4 ? 'var(--coral)' : 'var(--ink)')}`, 112, t, T[1] != null && i === 4 ? T[1] : null);
  }
  h += slot('n', '<b class="sw">निष्कर्ष</b>', 196, o.end ?? null, T[2]);
  item(id, { at: o.at, out: null, fx: 'fade' });
  return `<div id="stripWrap"><div id="${id}" class="it">${h}</div><div id="snow"></div></div>`;
}

// ------------------------------------------------------ components ----
const colorOf = c => ({ cream: 'var(--cream)', ink: 'var(--ink)', brass: 'var(--brass)', coral: 'var(--coral)', maroon: 'var(--maroon)', teal: 'var(--teal)' }[c] || c);
/** Anything of yours on the timeline. box(html, {at, out, x, y, w, h, cx, fx, rot, cue, cls, style, id}) */
export const box = (html, o) => K.el(o, 'bx', html, {});
/** Type straight on the wood (cream, with a dark edge) or on a card (pass color). font: head | body | num */
export function text(o) {
  const f = { head: `800 ${o.size || 72}px/1.18 Baloo,Hind`, body: `700 ${o.size || 46}px/1.3 Hind`, num: `400 ${o.size || 120}px/1.1 Yatra,Baloo` }[o.font || 'head'];
  const col = colorOf(o.color || 'cream');
  const edge = o.edge === false ? '' : 'paint-order:stroke fill;-webkit-text-stroke:' + (o.size > 100 ? 10 : 7) + 'px rgba(43,29,20,.85);';
  return K.el({ ...o, style: `font:${f};color:${col};${edge}${o.wrap ? '' : 'white-space:nowrap;'}${o.align ? `text-align:${o.align};` : ''}${o.style || ''}` }, 'tx', o.html, { fx: o.fx || 'press', cueKind: o.cueKind });
}
/** A cream card laid on the table: set down with a knock. kind: cream | brass | coral | dark. size = font px. */
export function tag(o) {
  const k = o.kind || 'cream';
  return K.el({ ...o, style: `font-size:${o.size || 52}px;${o.style || ''}` }, `tg tg_${k}`, o.html ?? o.text, { fx: o.fx || 'drop', cueKind: 'knock', rot: o.rot ?? 0 });
}
/** One row in the heading band (y 1085-1195), a cream card full width. */
export const band = o => tag({ x: 40, y: LOOK.band.y0, w: 1000, size: 64, ...o, style: `text-align:center;height:${LOOK.band.y1 - LOOK.band.y0}px;line-height:${LOOK.band.y1 - LOOK.band.y0 - 6}px;padding:0 20px;${o.style || ''}`, cls: `bandrow ${o.cls || ''}` });
/** A point's big card, laid on the disc while he names it (to-you scenes). */
export function pointCard(o) {
  const id = o.id || uid('pc'), n = o.n;
  const parts = [];
  item(`${id}_n`, { at: o.at, out: o.out, fx: 'pop' }); cue('chime', o.at);
  parts.push(`<div id="${id}_n" class="sub pcn ${n === 5 ? 'pcc' : ''}">${n}</div>`);
  const tt = o.atText ?? o.at;
  item(`${id}_t`, { at: tt, out: o.out, fx: 'drop' }); if (tt !== o.at) cue('knock', tt);
  parts.push(`<div id="${id}_t" class="sub pct" style="font-size:${o.size || 76}px">${o.text}</div>`);
  item(id, { at: Math.min(o.at, tt), out: o.out, fx: 'none' });
  return `<div id="${id}" class="it pc ${n === 5 ? 'pc5' : ''}" style="${K.pos({ cx: true, y: o.y ?? 250, ...o })}">${parts.join('')}</div>`;
}
/** A brass plaque, engraved: the big word, with an optional line under it. */
export const plaque = o => K.el({ ...o, style: `font-size:${o.size || 120}px;${o.style || ''}` }, 'pq', `${o.html ?? o.text}${o.sub ? `<small>${o.sub}</small>` : ''}`, { fx: o.fx || 'drop', cueKind: 'knock' });
/** A rubber stamp in maroon (or coral), slams in. */
export const stamp = o => K.el({ ...o, style: `font-size:${o.size || 76}px;--c:${colorOf(o.color || 'maroon')};${o.style || ''}` }, 'sp', o.html ?? o.text, { fx: 'slam', cueKind: 'stamp', rot: o.rot ?? -5 });
/** Words that arrive on his words, stacked or in a row. items: [{html, at}] */
export function words(o) {
  const id = o.id || uid('wd'), dir = o.row ? 'row' : 'column';
  const h = o.items.map((it, i) => { item(`${id}_${i}`, { at: it.at, out: o.out, fx: o.fx || 'drop' }); cue(o.cueKind || 'pluck', it.at, 0, { n: i }); return `<div id="${id}_${i}" class="sub wdi tg tg_${it.kind || o.kind || 'cream'}" style="font-size:${o.size || 52}px">${it.html}</div>`; }).join('');
  item(id, { at: Math.min(...o.items.map(i => i.at)), out: o.out, fx: 'none' });
  return `<div id="${id}" class="it wd" style="${K.pos(o)};flex-direction:${dir};gap:${o.gap ?? 18}px;align-items:${o.align || 'center'}">${h}</div>`;
}
/** An arrow drawn across the frame (draws on in 0.3 s). */
export function arrow(o) {
  const id = o.id || uid('ar'), dx = o.x2 - o.x1, dy = o.y2 - o.y1, len = Math.hypot(dx, dy), a = Math.atan2(dy, dx), hw = o.head || 26, sw = o.sw || 10;
  const hx = s => (o.x2 - hw * Math.cos(a) + s * hw * .6 * Math.sin(a)).toFixed(1) + ' ' + (o.y2 - hw * Math.sin(a) - s * hw * .6 * Math.cos(a)).toFixed(1);
  item(`${id}_s`, { at: o.at, out: o.out, fx: 'draw', len: Math.ceil(len), d: o.d ?? .3 });
  item(`${id}_h`, { at: o.at + (o.d ?? .3) - .05, out: o.out, fx: 'fade', d: .08 });
  return `<svg class="arw" width="1080" height="1920" fill="none" stroke="${colorOf(o.color || 'cream')}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">` +
    `<path id="${id}_s" class="svi" d="M${o.x1} ${o.y1} L${o.x2} ${o.y2}" stroke-dasharray="${Math.ceil(len)}" stroke-dashoffset="${Math.ceil(len)}"/>` +
    `<path id="${id}_h" class="svi" d="M${hx(1)} L${o.x2} ${o.y2} L${hx(-1)}"/></svg>`;
}
/** A picture file on the timeline (a CSS background). */
export function img(o) {
  const cls = K.imageClass(o.file, o.fit || 'contain');
  return K.el({ ...o, cls: `${cls} ${o.cls || ''}` }, 'bx', '', { fx: o.fx || 'drop', cueKind: o.cueKind ?? 'slide' });
}
/** A brass pin with a name tag. side: where the tag sits ('r' | 'l' | 'u' | 'd'). */
export function pin(o) {
  const id = o.id || uid('pn');
  item(`${id}_p`, { at: o.at, out: o.out, fx: 'drop' });
  item(`${id}_t`, { at: o.at + .08, out: o.out, fx: 'pop' });
  cue('knock', o.at);
  const off = { r: 'left:30px;top:-38px', l: 'right:30px;top:-38px', u: 'left:50%;bottom:34px;transform-origin:50% 100%', d: 'left:50%;top:30px' }[o.side || 'r'];
  const centre = o.side === 'u' || o.side === 'd' ? 'margin-left:-50%;' : '';
  return `<div id="${id}" class="pin" style="left:${o.x.toFixed(1)}px;top:${o.y.toFixed(1)}px"><i id="${id}_p" class="sub pinh"></i><span class="pint" style="${off}"><b id="${id}_t" class="sub tg tg_cream" style="font-size:${o.size || 44}px;${centre}">${o.name}</b></span></div>`;
}
export const mapAnchors = () => JSON.parse(fs.readFileSync(A('map.json'), 'utf8'));

// --------------------------------------------------------------- CSS ----
const fontCSS = () => {
  const F = LOOK.fonts, u = f => dataURL(path.join(K.ROOT, f), 'font/ttf');
  return `@font-face{font-family:Baloo;font-weight:400 800;src:url(${u(F.head[0])}) format('truetype')}` +
    `@font-face{font-family:Hind;font-weight:700;src:url(${u(F.body[0])}) format('truetype')}` +
    `@font-face{font-family:Yatra;font-weight:400;src:url(${u(F.num[0])}) format('truetype')}`;
};
const L = LOOK, W = L.window;
const baseCSS = () => `
:root{--wood:${L.wood};--wdk:${L.wood_dark};--brass:${L.brass};--bdk:${L.brass_dark};--cream:${L.cream};--ink:${L.ink};--maroon:${L.maroon};--coral:${L.coral};--teal:${L.teal};--bg:${L.cream}}
#st{font-family:Hind,sans-serif;color:var(--ink)}
/* under */
#tbl{position:absolute;inset:0}
#woodbg{position:absolute;inset:0;background:url(${dataURL(A('wood.png'), 'image/png')}) 0 0/1080px 1920px}
#tsvg,#tsvg2{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible}
#mapd{position:absolute;border-radius:50%;background:url(${dataURL(A('map_disc.png'), 'image/png')}) 50% 50%/cover;opacity:0}
#mapf{position:absolute;inset:0;background:url(${dataURL(A('map.png'), 'image/png')}) 0 0/1080px 1920px;opacity:0}
#seatbg{position:absolute;border-radius:50%;background:radial-gradient(circle,#6b2a2f 0,#4a171b 100%);box-shadow:0 0 0 12px var(--brass),0 0 0 16px var(--bdk),0 14px 24px 14px rgba(0,0,0,.35);opacity:0}
#ishadow{position:absolute;border-radius:50%;opacity:0;box-shadow:inset 0 0 34px 10px rgba(20,8,2,.55)}
/* overlay */
.arw{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;pointer-events:none}
.tx{color:var(--cream)}
.tg{background:var(--cream);color:var(--ink);font:800 52px/1.18 Baloo,Hind;padding:10px 26px 4px;border-radius:10px;box-shadow:0 6px 0 rgba(40,20,8,.25),0 10px 18px rgba(20,8,2,.35);white-space:nowrap}
.tg_brass{background:linear-gradient(180deg,#e9c35e,#c8962c);color:#3a2410}
.tg_coral{background:var(--coral);color:#fff7ee}
.tg_dark{background:#2b1d14;color:var(--cream)}
.tg_teal{background:var(--teal);color:#f3fbf6}
.wd{display:flex}
.pc{display:flex;flex-direction:column;align-items:center;gap:14px}
.pcn{font:400 120px/150px Yatra,Baloo;width:170px;height:170px;border-radius:50%;text-align:center;color:#3a2410;background:radial-gradient(circle at 40% 35%,#f3d27a,#c8962c 70%,#9c701c);box-shadow:0 0 0 6px #8a6218,0 12px 22px rgba(20,8,2,.45)}
.pcn.pcc{background:radial-gradient(circle at 40% 35%,#f59a80,#e2553f 70%,#b63a27);color:#fff7ee;box-shadow:0 0 0 6px #9c2f1f,0 12px 22px rgba(20,8,2,.45)}
.pct{background:var(--cream);color:var(--ink);font:800 76px/1.15 Baloo,Hind;padding:22px 40px 12px;border-radius:14px;text-align:center;box-shadow:0 8px 0 rgba(40,20,8,.25),0 14px 26px rgba(20,8,2,.4);max-width:980px;border-top:10px solid var(--brass)}
.pc5 .pct{border-top-color:var(--coral)}
.pq{font:800 120px/1.05 Baloo,Hind;color:#3a2410;text-align:center;padding:26px 60px 16px;border-radius:16px;background:linear-gradient(180deg,#f0cd6b 0,#d9a841 45%,#b8892c 100%);box-shadow:inset 0 3px 0 rgba(255,240,190,.7),inset 0 -4px 0 rgba(90,55,10,.5),0 0 0 5px #8a6218,0 14px 26px rgba(20,8,2,.45);text-shadow:0 2px 0 rgba(255,236,170,.55),0 -1px 0 rgba(70,40,5,.5);white-space:nowrap}
.pq small{display:block;font:700 46px/1.3 Hind;margin-top:6px}
.sp{--c:var(--maroon);border:7px solid var(--c);outline:3px solid var(--c);outline-offset:5px;border-radius:12px;padding:8px 30px 0;font:800 76px/1.15 Baloo,Hind;color:var(--c);white-space:nowrap;background:rgba(246,238,220,.88)}
.pin{position:absolute;width:0;height:0}
.pinh{position:absolute;left:-16px;top:-16px;width:32px;height:32px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff1b8,#d9a841 55%,#8a6218);box-shadow:0 4px 8px rgba(0,0,0,.55)}
.pint{position:absolute;white-space:nowrap}
.pint .tg{padding:6px 18px 0;display:inline-block}
/* the strip */
#stripWrap{position:absolute;left:0;top:${L.strip.y0}px;width:1080px;height:${L.strip.y1 - L.strip.y0}px}
#strip{left:0;top:0;width:1080px;height:100%;display:flex;justify-content:center;align-items:center;gap:12px}
.ss{position:relative;height:118px;border:4px dashed rgba(246,238,220,.55);border-radius:14px;box-sizing:border-box;background:rgba(30,15,6,.18)}
.sf{position:absolute;inset:-4px;border-radius:14px;background:var(--cream);display:flex!important;align-items:center;justify-content:center;gap:4px;box-shadow:0 5px 0 rgba(40,20,8,.25),0 8px 14px rgba(20,8,2,.35)}
.sf .sn{font:400 54px/1 Yatra,Baloo;color:#9c701c;margin-top:8px}
.sf .sw{font:800 44px/1 Baloo,Hind;color:var(--ink);margin-top:8px}
.stk{position:absolute;right:-12px;top:-18px;background:var(--cream);border-radius:50%;width:46px;height:46px;display:flex!important;align-items:center;justify-content:center;box-shadow:0 3px 6px rgba(0,0,0,.4)}
#snow{position:absolute;top:${(L.strip.y1 - L.strip.y0 - 132) / 2}px;height:132px;border:5px solid var(--brass);border-radius:18px;box-sizing:border-box;box-shadow:0 0 18px 4px rgba(240,200,90,.6);opacity:0}
#seatring{position:absolute;border-radius:50%;opacity:0}
`;

// ------------------------------------------------------------ browser ----
// The under layer and the strip glow, as pure functions of t. Shares the stage's helpers.
function UNDER(V) {
  const R = V.look.disc, SEATS = V.seats, TURNS = V.turns, CR = V.cracks;
  const discAt = t => glide(t, st => R[st]);
  const shotsAll = SC.flatMap(s => s.shots).sort((a, b) => a.t0 - b.t0);
  const IR = .28;
  function iris(t) {
    let o = 0;
    for (const s of shotsAll) if (t >= s.t0 && t < s.t1) o = Math.max(o, Math.min(eout(P(t, s.t0, s.t0 + IR)), 1 - ein(P(t, s.t1 - IR, s.t1))));
    return o;
  }
  function turnAngle(t) { let a = 0; for (const tt of TURNS) a += 45 * eio(P(t, tt, tt + .7)); return a; }
  // three crack courses across a unit disc (x, y in -1..1)
  const COURSE = [
    [[-1.02, -.3], [-.6, -.18], [-.42, -.34], [-.1, -.12], [.12, -.26], [.4, -.05], [.62, -.2], [1.02, -.08]],
    [[-.7, .78], [-.48, .5], [-.56, .3], [-.24, .14], [-.3, -.06], [-.02, -.32], [.06, -.64], [.3, -.98]],
    [[-.3, 1.0], [-.06, .7], [.2, .62], [.12, .38], [.42, .2], [.38, -.02], [.7, .1], [.98, .3]],
  ];
  const plateSVG = (x, y, ang, o) => '<g transform="translate(' + f1(x) + ' ' + f1(y) + ') rotate(' + f1(ang) + ')" opacity="' + f3(o) + '"><rect x="-40" y="-15" width="80" height="30" rx="7" fill="#c8962c" stroke="#8a6218" stroke-width="3"/><rect x="-30" y="-6" width="60" height="12" rx="3" fill="#e9c35e"/><rect x="-40" y="-15" width="80" height="6" rx="3" fill="#f3d27a" opacity=".7"/></g>';
  window.frameUnder = t => {
    const d = discAt(t), io = iris(t), hr = d.r * io;
    // the hole: everything on the table is masked out inside radius hr
    const m = hr > .5 ? 'radial-gradient(circle at ' + f1(d.cx) + 'px ' + f1(d.cy) + 'px, transparent ' + f1(hr) + 'px, #000 ' + f1(hr + .8) + 'px)' : 'none';
    const tb = $('tbl'); tb.style.webkitMaskImage = m; tb.style.maskImage = m;
    let s = '';
    // shadow of the table rim on the wood, the leather disc, the brass ring
    s += '<circle cx="' + f1(d.cx) + '" cy="' + f1(d.cy + 10) + '" r="' + f1(d.r + 30) + '" fill="rgba(25,10,3,.35)"/>';
    s += '<circle cx="' + f1(d.cx) + '" cy="' + f1(d.cy) + '" r="' + f1(d.r) + '" fill="url(#lth)"/>';
    s += '<circle cx="' + f1(d.cx) + '" cy="' + f1(d.cy) + '" r="' + f1(d.r + 12) + '" fill="none" stroke="url(#brs)" stroke-width="24"/>';
    s += '<circle cx="' + f1(d.cx) + '" cy="' + f1(d.cy) + '" r="' + f1(d.r + 24) + '" fill="none" stroke="#6e4a12" stroke-width="3"/>';
    s += '<circle cx="' + f1(d.cx) + '" cy="' + f1(d.cy) + '" r="' + f1(d.r) + '" fill="none" stroke="#7a5412" stroke-width="3"/>';
    // the ring lights up all the way round
    for (const g of V.glow) { if (t < g.t || (g.out != null && t >= g.out)) continue; const p = eio(P(t, g.t, g.t + 1.2)), C = 2 * Math.PI * (d.r + 12);
      s += '<circle cx="' + f1(d.cx) + '" cy="' + f1(d.cy) + '" r="' + f1(d.r + 12) + '" fill="none" stroke="#fff0b0" stroke-width="12" stroke-dasharray="' + f1(C * p) + ' ' + f1(C) + '" transform="rotate(-90 ' + f1(d.cx) + ' ' + f1(d.cy) + ')" opacity=".85" filter="url(#gl)"/>'; }
    // cracks
    for (const c of CR) { const p = P(t, c.t, c.t + .45), heal = c.out == null ? 1 : 1 - P(t, c.out, c.out + .8); if (p <= 0 || heal <= 0) continue; const pts = COURSE[c.i].map(([x, y]) => [d.cx + x * d.r * .96, d.cy + y * d.r * .96]);
      let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      const dd = 'M' + pts.map(q => f1(q[0]) + ' ' + f1(q[1])).join(' L');
      s += '<path d="' + dd + '" fill="none" stroke="#1a0a05" stroke-width="16" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="' + f1(L) + '" stroke-dashoffset="' + f1(L * (1 - eout(p))) + '" opacity="' + f3(heal * .7) + '"/>' +
        '<path d="' + dd + '" fill="none" stroke="' + V.look.coral + '" stroke-width="7" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="' + f1(L) + '" stroke-dashoffset="' + f1(L * (1 - eout(p))) + '" opacity="' + f3(heal) + '"/>'; }
    // the eight plates: scattered on the disc, then round the ring; they turn with the table
    if (SEATS && t >= (SEATS.from ?? SEATS.t0)) {
      const p = SEATS.t1 > SEATS.t0 ? eio(P(t, SEATS.t0, SEATS.t1)) : 1, rot = turnAngle(t), fin = SEATS.from == null ? 1 : P(t, SEATS.from, SEATS.from + .3);
      for (let i = 0; i < 8; i++) {
        const a = (-90 + i * 45 + 22.5 + rot) * Math.PI / 180, ext = d.r + 44;
        const sx = d.cx + ext * Math.cos(a), sy = d.cy + ext * Math.sin(a), sa = (-90 + i * 45 + 22.5 + rot) + 90;
        const fx = d.cx + V.scatter[i][0] * d.r, fy = d.cy + V.scatter[i][1] * d.r, fa = (i % 3 - 1) * 14;
        s += plateSVG(lerp(fx, sx, p), lerp(fy, sy, p), lerp(fa, sa, p), fin);
      }
    }
    $('tg').innerHTML = s;
    // the inner shadow round an open picture
    const sh = $('ishadow'); sh.style.left = f1(d.cx - d.r) + 'px'; sh.style.top = f1(d.cy - d.r) + 'px'; sh.style.width = sh.style.height = f1(2 * d.r) + 'px'; sh.style.opacity = f3(io);
    // the inlaid map, inside the disc and over the whole frame
    let md = 0; for (const [a, b] of V.mapDisc) md = Math.max(md, env(t, a, b, .35, .3));
    const e = $('mapd'); e.style.opacity = f3(md); e.style.left = f1(d.cx - d.r) + 'px'; e.style.top = f1(d.cy - d.r) + 'px'; e.style.width = e.style.height = f1(2 * d.r) + 'px';
    e.style.transform = 'scale(' + f3(.9 + .1 * md) + ')';
    let mf = 0; for (const [a, b] of V.mapFull) mf = Math.max(mf, env(t, a, b, .45, .4));
    $('mapf').style.opacity = f3(mf);
    // the round seat he sits in through the recap
    const sm = glide(t, st => st === 'small' ? 1 : 0), S = V.look.seat, sb = $('seatbg');
    sb.style.opacity = f3(sm); sb.style.left = f1(S.cx - S.r) + 'px'; sb.style.top = f1(S.cy - S.r) + 'px'; sb.style.width = sb.style.height = f1(2 * S.r) + 'px';
    sb.style.transform = 'scale(' + f3(.6 + .4 * sm) + ')';
  };
  // the presenter's round seat: the mask is a circle in the "small" state
  const seatClip = t => { const sm = glide(t, st => st === 'small' ? 1 : 0), S = V.look.seat; if (sm <= 0) return 'none';
    const r = lerp(1500, S.r - 4, sm), cx = lerp(540, S.cx, sm), cy = lerp(1200, S.cy, sm); return 'circle(' + f1(r) + 'px at ' + f1(cx) + 'px ' + f1(cy) + 'px)'; };
  window.frameMask = t => { $('mk').style.clipPath = seatClip(t); };
  window.framePreview = t => {
    const c = seatClip(t), pv = $('pv_pres');
    if (c === 'none') { pv.style.clipPath = 'none'; return; }
    // the clip is in frame pixels; the preview cut-out is transformed, so clip its parent box instead
    $('pvclip').style.clipPath = c;
  };
  // the strip: hidden while the map or the cracked table has the screen; a glow on the slot he is on
  const NOW = V.now || [];
  window.frameStrip = t => {
    const w = $('stripWrap'); if (!w) return;
    w.style.opacity = f3(glide(t, st => st === 'hidden' ? 0 : 1));
    let k = null; for (const [tt, kk] of NOW) if (t >= tt) k = kk;
    const n = $('snow');
    if (k == null || k === 'off') { n.style.opacity = '0'; return; }
    const sl = $('strip_s' + k), r = sl.getBoundingClientRect(), pr = w.getBoundingClientRect(), z = pr.width / 1080;
    n.style.left = f1((r.left - pr.left) / z - 9) + 'px'; n.style.width = f1(r.width / z + 18) + 'px'; n.style.opacity = '1';
  };
}

/** The page. html = overlay markup; css = extra; js = browser(...) code that may set window.frame(t). */
export function stage({ css = '', html = '', js = '', part }) {
  // every round picture opens and closes like an iris
  for (const sc of K.REG.spec.scenes) for (const x of sc.shots) cue('iris', x.t0, .28);
  const under = `<div id="tbl"><div id="woodbg"></div><svg id="tsvg" viewBox="0 0 1080 1920"><defs>
<radialGradient id="lth" cx="45%" cy="40%" r="70%"><stop offset="0" stop-color="#74303a"/><stop offset=".7" stop-color="#5c1f24"/><stop offset="1" stop-color="#3e1216"/></radialGradient>
<linearGradient id="brs" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f3d27a"/><stop offset=".35" stop-color="#c8962c"/><stop offset=".6" stop-color="#e9c35e"/><stop offset="1" stop-color="#8a6218"/></linearGradient>
<filter id="gl" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter></defs><g id="tg"></g></svg><div id="mapd"></div></div>
<div id="ishadow"></div><div id="seatbg"></div><div id="mapf"></div>`;
  const data = { look: { disc: LOOK.disc, seat: LOOK.seat, coral: LOOK.coral }, seats: TBL.seats, turns: TBL.turns, cracks: TBL.cracks, glow: TBL.glow,
    mapDisc: TBL.mapDisc, mapFull: TBL.mapFull, scatter: SCATTER, now: STRIP.now || [] };
  const js0 = `;(${UNDER.toString()})(D.v);window.frame=(f=>t=>{window.frameStrip(t);if(f)f(t);})(null);`;
  // a part's own frame(t) is chained after the strip's
  const js1 = js ? `;(()=>{const __a=window.frame;${js};const __b=window.frame;window.frame=__b===__a?__a:(t=>{__a(t);__b(t);});})();` : '';
  return K.stage({ fontCSS: fontCSS(), css: baseCSS() + '#pvclip{position:absolute;inset:0;display:contents}' + css, under, overlay: html, js: js0 + js1, data,
    fonts: ['800 40px Baloo', '400 40px Baloo', '700 40px Hind', '400 40px Yatra'] }).replace('<div id="pv_pres"></div>', '<div id="pvclip" style="position:absolute;inset:0"><div id="pv_pres"></div></div>');
}
/** Wrap your own browser code: browser(function (T) { window.frame = t => {...} }, data). */
export const browser = (fn, data = {}) => `(${fn.toString()})(${JSON.stringify(data)});`;
export const cli = K.cli;
