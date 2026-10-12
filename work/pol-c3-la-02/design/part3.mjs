// POL-C3-LA-02 part 3: भारत की भूमिका, then the whole answer redrawn. 11 scenes on the kit, no Veo shots.
//
//   node work/pol-c3-la-02/design/part3.mjs            -> out/layers/p3/{under,mask,overlay}.mov
//   node work/pol-c3-la-02/design/part3.mjs --cues     -> out/cues_p3.json
//   node work/pol-c3-la-02/design/part3.mjs --sheet    -> out/stills/p3/sheet_p3.png
//   node work/pol-c3-la-02/design/part3.mjs --stills 24.9,99.8 [--full]
//
// Every time is asked of the word clock by quoting what he says (s.at('...')), scoped to the scene.
// Only layout is decided here. Free zones per presenter state: look.json "place".
import fs from 'node:fs';
import path from 'node:path';
import { VIDEO, LOOK, load, stage, cli, line, item, cue, pips, heading, slip, stamp, text, box, wash, skeleton, tiles, sym, crown, arrow, img, mapPt } from './kit.mjs';

// THE ONE SWITCH for the recap's thumbnails: true = a point's still is shown at the end of its row
// IF its file exists (out/stills/V*.png, cut from the Veo clips). The layout is complete without them.
const USE_STILLS = true;
const STILL_OF = ['V4', 'V5', 'V6', 'V8', 'V9', 'V10'];   // point 1..6 -> the picture that point was taught with

const { S, at, scope, dur } = load(3);
const INK = ['blue', 'red', 'blue', 'blue', 'blue', 'blue'];   // whose point each of the six is
let H = '', s;

// ------------------------------------------------------------ helpers ----
const sub = (id, html, t, o = {}) => { item(id, { at: t, out: o.out, fx: o.fx || 'fade', hold: o.hold, d: o.d }); if (o.cue) cue(o.cue, t); return `<span id="${id}" class="sub ${o.cls || ''}" style="${o.style || ''}">${html}</span>`; };
// words that land one after another on one row (band y 1040-1175)
const seq = (id, parts, o = {}) => box(parts.map((p, i) => sub(`${id}_${i}`, p.html, p.at, { fx: 'press', cue: 'stamp', cls: `${p.ink || o.ink || 'ink'} ${p.cls || ''}`, hold: o.hold, d: o.d, out: o.out })).join(''),
  { x: 0, w: 1080, y: 1058, ...o, id, at: Math.min(...parts.map(p => p.at)), fx: 'none', cls: 'brow', style: `font-size:${o.size || 80}px` });
// A straight arrow that does not fade (kit arrow() fades out, which costs six frames of map).
function arr(id, x1, y1, x2, y2, t, o = {}) {
  const a = Math.atan2(y2 - y1, x2 - x1), hw = o.head || 36, d = o.d ?? .13;
  const hp = k => `${(x2 - hw * Math.cos(a) + k * hw * .62 * Math.sin(a)).toFixed(1)} ${(y2 - hw * Math.sin(a) - k * hw * .62 * Math.cos(a)).toFixed(1)}`;
  item(`${id}_s`, { at: t, out: o.out, fx: 'draw', len: 100, d, hold: true });
  item(`${id}_h`, { at: t + d, out: o.out, fx: 'none', hold: true });
  cue('scratch', t, .25);
  return `<svg class="arw ${o.ink || 'blue'}" width="1080" height="1920" fill="none" stroke="currentColor" stroke-width="${o.sw || 14}" stroke-linecap="round" stroke-linejoin="round">` +
    `<path id="${id}_s" class="svi" d="M${x1} ${y1} L${x2} ${y2}" pathLength="100" stroke-dasharray="100 200" stroke-dashoffset="100"/><path id="${id}_h" class="svi" d="M${hp(1)} L${x2} ${y2} L${hp(-1)}"/></svg>`;
}
// THE MAP, held. A photograph costs over a megabyte for every frame that changes while it is on, so here it
// cuts in and out with its two plates (kit map() glides in and fades out), and nothing over it moves for long.
const W = LOOK.window;
function mapHeld(id, t0, t1, labels) {
  let h = img({ id, file: path.join(VIDEO, 'assets/map.png'), at: t0, out: t1, x: W.x, y: W.y, w: W.w, h: W.h, fx: 'none', hold: true, cue: 'slide', style: 'border:5px solid var(--ink);background-size:cover' });
  for (const [k, lb] of [['nepal', 'नेपाल'], ['india', 'भारत']]) {
    if (labels[k] == null) continue;
    const p = mapPt(k);   // the plate is paper-coloured: the नेपाल anchor sits on the darkest ink of the relief
    h += box(lb, { id: `${id}_${k}`, at: labels[k], out: t1, x: p.x, y: p.y, cls: 'mpl', style: 'transform-origin:0 0;margin:-42px 0 0 -90px;width:180px;text-align:center', fx: 'press', d: .07, hold: true, cue: 'stamp' });
  }
  return h;
}
const upArrow = sz => `<span class="upa">${arrow({ size: sz, sw: 12 })}</span>`;

// flat symbols for the four agreements, cream on the tile (viewBox 0 0 100 100)
const ICO = {
  rail: `<path d="M38 6 L16 96 M62 6 L84 96" fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round"/><path d="M30 20 H70 M26 38 H74 M21 57 H79 M15 78 H85" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/>`,
  plane: `<g transform="rotate(45 50 50)"><path d="M50 2 C56 2 59 12 59 22 V38 L98 62 V73 L59 62 V80 L72 90 V98 L50 92 L28 98 V90 L41 80 V62 L2 73 V62 L41 38 V22 C41 12 44 2 50 2 Z"/></g>`,
  college: `<path d="M6 36 L50 8 L94 36 Z"/><rect x="10" y="40" width="80" height="9"/><rect x="16" y="53" width="11" height="28"/><rect x="36" y="53" width="11" height="28"/><rect x="53" y="53" width="11" height="28"/><rect x="73" y="53" width="11" height="28"/><rect x="8" y="84" width="84" height="7"/><rect x="2" y="93" width="96" height="6"/>`,
  hall: `<path d="M2 48 Q50 2 98 48 V56 H2 Z"/><path fill-rule="evenodd" d="M7 60 H93 V96 H7 Z M17 96 V78 a7 7 0 0 1 14 0 V96 Z M43 96 V76 a7 7 0 0 1 14 0 V96 Z M69 96 V78 a7 7 0 0 1 14 0 V96 Z"/>`,
};
const ico = (k, sz = 112) => `<svg class="tsy" width="${sz}" height="${sz}" viewBox="0 0 100 100" fill="currentColor">${ICO[k]}</svg>`;

// --------------------------------------------------------- THE LINE ----
// The recap's page: the line above, the six rows of the answer under it (all above y 1380).
const RECAP = { x: 190, y: 420, w: 740, h: 290, yf: 56, row: 0, af: 44, tf: 72, sw: 13, r: 17, a: 1 };
{
  // s1: the route is known from parts 1 and 2 (pencilled, every year named); it is inked again, fast, on his words
  line.start({ ink: 0, pencil: '2015', named: ['1990', '2002', '2006', '2008', '2015'], title: true, mode: 'mid' });
  const a = (p, o) => at('s1', p, o);
  line.ink('1990', a('1990'), .3);
  line.ink('2008', a('संविधान'), a('2008') - a('संविधान') + .1);
  line.ink('2015', a('राजशाही'), .5);
  line.mode(S.s2.t0, 'strip');
  // s7: the page clears to an empty line; s8: it is drawn again, one stretch per point
  line.mode(S.s7.t0, RECAP).clear(S.s7.t0);
  const r = (p, o) => at('s8', p, o);
  line.ink('1990', r('पहला'), .4).name('1990', r('1990'));
  line.ink('peak', r('जन-आंदोलन'), 1).ink('edge', r('लोकतांत्रिक'), .6);
  line.name('2002', r('2002')).ink('2002', r('राजा'), .7, { drop: true }).ink('floor', r('लोकतंत्र'), .5);
  line.name('2006', r('2006')).ink('2006', r('जन-आंदोलन', { nth: 2 }), 1);
  const u6 = line.u('2006'), us = line.u('sabha'), u8 = line.u('2008');   // the three groups lift it a third each
  line.ink(u6 + (us - u6) / 3, r('सात'), .35).ink(u6 + (us - u6) * 2 / 3, r('माओवादी'), .35).ink('sabha', r('सामाजिक'), .35);
  line.mark('sabha', r('संविधान-सभा')).ink(us + (u8 - us) * .7, r('लोकतांत्रिक', { nth: 2 }), .5);
  line.ink('2008', r('28'), .6).name('2008', r('2008'));
  line.ink('2015', r('2015'), .7).name('2015', r('2015'));
  wash('red', r('दूसरा'), r('तीसरा') - .15);
  // s10: back to the strip; s11: the finished line, held
  line.mode(S.s10.t0, 'strip');
  line.mode(at('s11', 'वाली'), 'mid');
}

// ---- s1 · to you · the finished line, drawn fast; six pips full
s = scope('s1');
{
  const p0 = s.at('छहों'), p1 = s.at('points', { end: true });
  H += pips({ at: 0, out: S.s7.t0, fill: [0, 1, 2, 3, 4, 5].map(i => p0 + (p1 - p0) * i / 5) });
}
H += slip({ text: 'पिछले दो parts में', at: s.at('पिछले'), x: 60, y: 92 });

// ---- s2 · to you · heading भारत की भूमिका
s = scope('s2');
H += slip({ text: 'answer का आखिरी हिस्सा', at: s.at('आखिरी'), x: 70, y: 312 });
H += text({ html: 'नेपाल में <b class="blue">लोकतंत्र</b> की स्थापना में', size: 68, at: s.at('नेपाल'), x: 70, y: 436 });
H += heading({ text: 'भारत की भूमिका', at: s.at('भारत की भूमिका'), x: 70, y: 540 });

// ---- s3-s5 · explaining · the section's name and what it has covered so far, in the left column
const SEC_OUT = S.s6.t0;
H += box('भारत की भूमिका', { at: S.s3.t0, out: SEC_OUT, x: 46, y: 1206, cls: 'sech', fx: 'press', d: .07, hold: true });
const done = (i, label, t) => box(`${sym('tick', { size: 46, ink: 'blue' })}<span>${label}</span>`, { at: t, out: SEC_OUT, x: 52, y: 1316 + i * 94, cls: 'secr', fx: 'press', d: .07, hold: true, cue: 'tick' });

// ---- s3 · THE MAP: three arrows rise from भारत to नेपाल
s = scope('s3');
{
  const N = mapPt('nepal'), I = mapPt('india'), tN = [s.at('नैतिक'), s.at('राजनीतिक'), s.at('कूटनीतिक')];
  H += mapHeld('m3', s.t0, s.t1, { india: s.at('भारत'), nepal: s.at('नेपाल') });
  H += slip({ text: 'पड़ोसी होने के नाते', at: s.at('पड़ोसी'), out: tN[0], x: 64, y: 1066, d: .1, hold: true });
  // from the plain beside भारत up to the hills under नेपाल, left to right in the order he names them
  [[I.x + 132, I.y - 30, N.x - 118, N.y + 46], [I.x + 262, I.y - 6, N.x + 12, N.y + 64], [I.x + 396, I.y + 26, N.x + 150, N.y + 116]].forEach((p, i) => { H += arr(`a3_${i}`, ...p, tN[i]); });
  H += seq('n3', [{ html: 'नैतिक', at: tN[0] }, { html: '<i>·</i>राजनीतिक', at: tN[1] }, { html: '<i>·</i>कूटनीतिक', at: tN[2] }, { html: 'समर्थन', at: s.at('समर्थन'), cls: 'blk' }], { ink: 'blue', size: 66, hold: true, d: .07 });
  H += done(0, 'समर्थन', s.at('समर्थन'));
}

// ---- s4 · four agreements fill in; a signature under all four; then the heading
s = scope('s4');
H += tiles({ at: s.t0 + .1, x: 80, y: 306, w: 920, cols: 2, th: 268, gap: 20, size: 54, items: [
  { html: `${ico('rail')}रेल सेवा`, at: s.at('रेल') },
  { html: `${ico('plane')}नागरिक विमान सेवा`, at: s.at('नागरिक') },
  { html: `${ico('college')}पॉलिटेक्निक कॉलेज`, at: s.at('पॉलिटेक्निक') },
  { html: `${ico('hall')}कन्वेंशन हॉल`, sub: 'सीमा पर', at: s.at('कन्वेंशन') },
] });
H += slip({ html: 'नई <b class="blue">लोकतांत्रिक</b> सरकार के साथ', at: s.at('नई'), out: s.at('जैसे'), x: 64, y: 1066 });
H += seq('h4', [{ html: 'विकास कार्यों के', at: s.at('विकास') }, { html: 'समझौते', at: s.at('समझौते') }]);
{
  const t = s.at('समझौते');
  item('sig4', { at: t, fx: 'draw', len: 100, d: .7 }); cue('scratch', t, .7);
  H += `<svg class="arw ink" width="1080" height="1920" fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"><path id="sig4" class="svi" pathLength="100" stroke-dasharray="100 200" stroke-dashoffset="100" ` +
    `d="M300 996 C314 946 338 940 332 974 C326 1006 306 1000 328 972 C352 942 372 946 364 978 C360 996 376 990 388 972 C400 952 414 956 410 976 C420 954 436 952 440 972 C446 986 458 980 466 968 C478 950 492 958 488 976 C560 990 690 984 790 962"/></svg>`;
  H += done(1, 'समझौते', t);
}

// ---- s5 · the map again: two name plates (type only), a dashed path from नेपाल to भारत for each
s = scope('s5');
{
  const K = mapPt('kathmandu'), D = mapPt('delhi'), o = { hold: true, d: .07 };
  H += mapHeld('m5', s.t0, s.t1, { nepal: s.t0, india: s.t0 });
  const plate = (id, title, name, tT, tN, x, y) => box(sub(`${id}_t`, title, tT, { ...o, cls: 'plt', fx: 'none' }) + sub(`${id}_n`, name, tN, { ...o, cls: 'pln', fx: 'press', cue: 'stamp' }),
    { id, at: tT, x, y, cls: 'pl nm', ink: 'ink', fx: 'press', ...o, cue: 'slide' });
  H += plate('pm', 'प्रधानमंत्री', 'प्रचंड', s.at('प्रधानमंत्री'), s.at('प्रचंड'), 700, 316);
  H += slip({ text: '= पुष्प कमल दहल', at: s.at('पुष्प'), x: 616, y: 480, from: 'R', ...o });
  H += plate('pr', 'राष्ट्रपति', 'रामबरन यादव', s.at('राष्ट्रपति'), s.at('रामबरन'), 580, 748);
  // the two visits: Kathmandu -> Delhi, one path each, through the plain
  const path2 = (id, cx, cy, sy, ex, ey, t) => {
    const x0 = K.x + 4, y0 = K.y + sy, a = Math.atan2(ey - cy, ex - cx), hw = 30, d = `M${x0} ${y0} Q${cx} ${cy} ${ex} ${ey}`;
    const hp = k => `${(ex - hw * Math.cos(a) + k * hw * .62 * Math.sin(a)).toFixed(1)} ${(ey - hw * Math.sin(a) - k * hw * .62 * Math.cos(a)).toFixed(1)}`;
    item(`${id}_m`, { at: t, fx: 'draw', len: 100, d: .2, hold: true }); item(`${id}_p`, { at: t, fx: 'none', hold: true }); item(`${id}_h`, { at: t + .2, fx: 'none', hold: true }); cue('scratch', t, .4);
    return `<svg class="arw ink" width="1080" height="1920" fill="none" stroke="currentColor" stroke-width="9" stroke-linejoin="round"><defs><mask id="${id}_k" maskUnits="userSpaceOnUse" x="0" y="0" width="1080" height="1920">` +
      `<path id="${id}_m" d="${d}" pathLength="100" stroke="#fff" stroke-width="26" stroke-dasharray="100 200" stroke-dashoffset="100"/></mask></defs>` +
      `<path id="${id}_p" class="svi" d="${d}" stroke-dasharray="22 15" mask="url(#${id}_k)"/><path id="${id}_h" class="svi" stroke-linecap="round" d="M${hp(1)} L${ex} ${ey} L${hp(-1)}"/></svg>`;
  };
  H += path2('v5a', 430, 704, 12, D.x + 14, D.y - 36, s.at('भारत'));
  H += path2('v5b', 415, 818, 26, D.x - 4, D.y + 36, s.at('यात्राएँ'));
  H += seq('h5', [{ html: 'भारत यात्राएँ', at: s.at('भारत') }], { size: 84, ...o });
  H += done(2, 'यात्राएँ', s.at('यात्राएँ'));
}

// ---- s6 · to you · the line to write, in the exam serif
s = scope('s6');
H += slip({ html: 'भारत यात्राएँ = <b>स्पष्ट प्रमाण</b>', size: 50, at: s.at('स्पष्ट'), x: 70, y: 306 });
H += box('<div class="cdl">भारत ने नेपाल में</div>' +
  [['<span class="blue">लोकतंत्र</span> की बहाली', s.at('लोकतंत्र')], ['+ रिश्ते मज़बूत', s.at('रिश्ते')], ['= महत्वपूर्ण भूमिका', s.at('महत्वपूर्ण')]].map(([h, t], i) => sub(`c6_${i}`, h, t, { cls: `c6 c6_${i}`, cue: 'scratch' })).join(''),
  { at: s.at('भारत'), x: 70, y: 424, w: 940, cls: 'cd', fx: 'slideU', cue: 'slide' });

// ---- s7 · hidden · the page clears: an empty line and six empty rows
// ---- s8 · small · THE WHOLE ANSWER: one stretch of the line and one row per point, held to the end of s9
const RC = { x: 60, y: 862, w: 960, rh: 86, out: S.s9.t1 };
{
  const s7 = scope('s7'), r = (p, o) => at('s8', p, o), out = RC.out;
  const ORD = ['पहला', 'दूसरा', 'तीसरा', 'चौथा', 'पाँचवाँ', 'छठा'].map(w => r(w));
  H += pips({ at: s7.t0, out: null, fill: ORD });
  const yr = (h, t) => ({ h, t, cls: 'ryr' }), tx = (h, t) => ({ h, t, cls: 'rtx' }), grp = t => ({ h: sym('people', { size: 54 }), t, cls: 'rgp', fx: 'pop' });
  const ROWS = [
    [yr('1990', r('1990')), tx('संविधान', r('संविधान'))],
    [yr('2002', r('2002')), tx('संसद भंग', r('संसद भंग'))],
    [yr('अप्रैल 2006', r('अप्रैल')), tx('जन-आंदोलन,', r('जन-आंदोलन', { nth: 2 })), tx('संसद बहाल', r('संसद की बहाली'))],
    [grp(r('सात')), grp(r('माओवादी')), grp(r('सामाजिक')), tx('तीन गुट:', r('कार्यकर्ताओं')), tx('अहिंसक नेतृत्व', r('अहिंसक'))],
    [tx('संविधान-सभा', r('संविधान-सभा')), tx('का गठन', r('गठन'))],
    [yr('28 मई 2008', r('28')), { h: '', t: 0, crown: [r('राजशाही'), r('अंत'), r('नेपाल')] }, tx('गणराज्य,', r('गणराज्य')), yr('2015', r('2015')), tx('संविधान', r('संविधान', { nth: 2 }))],
  ];
  let rows = '';
  ROWS.forEach((row, k) => {
    cue('tick', ORD[k]);
    let h = `<span class="rslot">${k + 1}${sub(`rc${k}`, k + 1, ORD[k], { out, fx: 'pop', cls: 'rchip' })}</span>`;
    row.forEach((p, j) => {
      if (p.crown) {   // राजशाही का अंत: the crown stands where गणराज्य will be written, is struck out, and goes
        const [t0, tx_, t1] = p.crown;
        item(`rcr_x`, { at: tx_, out: t1, fx: 'draw', len: 100, d: .2 }); cue('scratch', tx_, .2);
        h += `<span class="rcrw">${sub('rcr', crown({ size: 62 }) + `<svg class="rcx" width="76" height="76" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="11" stroke-linecap="round"><path id="rcr_x" class="svi" pathLength="100" stroke-dasharray="100 200" stroke-dashoffset="100" d="M10 88 L90 12"/></svg>`, t0, { out: t1, fx: 'pop', cue: 'tick' })}</span>`;
        return;
      }
      h += sub(`rp${k}_${j}`, p.h, p.t, { out, fx: p.fx || 'press', cls: p.cls, cue: p.cls === 'rgp' ? 'tick' : 'stamp' });
    });
    rows += `<div class="rr ${INK[k]}">${h}</div>`;
    const f = path.join(VIDEO, `out/stills/${STILL_OF[k]}.png`);
    if (USE_STILLS && fs.existsSync(f)) H += img({ file: f, at: ORD[k], out, x: RC.x + RC.w - 138, y: RC.y + k * RC.rh + 5, w: 138, h: 76, fx: 'pop', ink: INK[k], style: 'background-size:cover;border:4px solid var(--c)' });
  });
  H += box(rows, { at: s7.at('क्रम'), out, x: RC.x, y: RC.y, w: RC.w, cls: 'rc', fx: 'fade', cue: 'slide' });
  // the same numbers beside their stretches of the line
  const CH = [['1990', 'peak', -52, -14, r('जन-आंदोलन')], ['edge', '2002', 54, -10, r('राजा')], ['floor', '2006', 58, 34, r('जन-आंदोलन', { nth: 2 })],
    ['2006', 'sabha', -52, -16, r('सात')], ['sabha', '2008', -52, -18, r('संविधान-सभा')], ['2008', '2015', 0, -50, r('28')]];
  CH.forEach(([a, b, dx, dy, t], k) => {
    const p = line.pt(a, RECAP), q = line.pt(b, RECAP);
    H += box(k + 1, { at: t, out, x: (p.x + q.x) / 2 + dx - 26, y: (p.y + q.y) / 2 + dy - 26, cls: 'lchip', ink: INK[k], fx: 'pop' });
  });
}

// ---- s9 · small · + भारत की भूमिका: the three arrows land beside the finished line
s = scope('s9');
{
  const tN = [s.at('नैतिक'), s.at('राजनीतिक'), s.at('कूटनीतिक')], e = line.pt('2015', RECAP);
  tN.forEach((t, i) => { H += arrow({ x1: e.x + 40 + i * 30, y1: e.y + 210, x2: e.x + 40 + i * 30, y2: e.y + 40, ink: 'blue', at: t, sw: 9, head: 20, d: .25 }); cue('scratch', t, .25); });
  H += box(`<div class="r7h">${sub('r7p', '+', s.at('आखिर'), { fx: 'pop', cls: 'r7c', cue: 'tick' })}${sub('r7t', 'भारत की भूमिका', s.at('भारत'), { fx: 'press', cue: 'stamp' })}</div>` +
    `<div class="r7l blue">${[['नैतिक', tN[0]], ['राजनीतिक', tN[1]], ['कूटनीतिक', tN[2]]].map(([w, t], i) => sub(`r7_${i}`, upArrow(40) + w, t, { fx: 'press' })).join('')}${sub('r7s', 'समर्थन', s.at('समर्थन'), { fx: 'press', cls: 'blk', cue: 'stamp' })}</div>`,
    { at: s.at('आखिर'), x: 560, y: 1394, w: 480, cls: 'r7', fx: 'none' });
}

// ---- s10 · to you · the skeleton ticked, 4 नंबर पक्के, Notes · held a breath into s11, then the finished line
s = scope('s10');
{
  const out = at('s11', 'पढ़ाई');
  H += skeleton({ at: [s.at('पृष्ठभूमि'), s.at('छह'), s.at('भारत')], ticks: [s.at('पृष्ठभूमि', { end: true }), s.at('points', { end: true }), s.at('भूमिका', { end: true })], out, x: 70, y: 292, w: 700 });
  H += stamp({ text: '4 नंबर पक्के', size: 76, at: s.at('पक्के'), out, x: 78, y: 662 });
  H += slip({ html: `exam में answer<br>${sub('nt10', `${arrow({ size: 46, sw: 11 })} <b>Notes</b> में`, s.at('Notes'), { out, fx: 'press', cue: 'tick' })}`, at: s.at('exam'), out, x: 612, y: 654, from: 'R' });
}

const css = `
.brow{display:flex;justify-content:center;align-items:center;gap:.3em;font:700 80px/1.2 Khand,Mukta;white-space:nowrap}
.brow .sub{color:var(--c)}.brow i{font-style:normal;margin-right:.3em;opacity:.6}
.blk{background:var(--c);color:var(--paper)!important;padding:.1em .3em 0}
.sech{background:var(--ink);color:var(--paper);font:700 60px/1 Khand,Mukta;padding:16px 16px 8px;white-space:nowrap}
.secr{display:flex;align-items:center;gap:16px;font:700 62px/1.1 Khand,Mukta;white-space:nowrap}.secr span{padding-top:6px}
.tsy{display:block;margin:0 auto 6px}
.pl.nm{padding:8px 28px 2px}.pl.nm .plt,.pl.nm .pln{display:block}.pl.nm .pln{font-size:80px}
.c6{display:block}.c6_2{border-top:3px solid var(--ink);margin-top:4px}
.sk .skr{height:100px;margin-bottom:14px;font-size:64px}.sk .skr>b{width:80px;font-size:64px}.sk .skk{width:70px;height:70px}
.rr{display:flex;align-items:center;gap:16px;height:86px;box-sizing:border-box;white-space:nowrap;border-bottom:3px dashed rgba(27,26,23,.22)}
.rslot{position:relative;flex:none;width:64px;height:64px;box-sizing:border-box;border:3px dashed rgba(27,26,23,.45);color:rgba(27,26,23,.45);font:700 46px/64px Khand;text-align:center;margin-right:4px}
.rchip{position:absolute;inset:-3px;background:var(--c);color:var(--paper);font:700 50px/70px Khand;text-align:center}
.ryr{font:700 60px/1 Khand,Mukta;color:var(--c);padding-top:8px}.rtx{font:800 46px/1.2 Mukta}.rgp{color:var(--c);margin-right:-8px}
.rcrw{position:relative;width:0;height:62px}.rcrw .sub{position:absolute;left:0;top:0}.rcx{position:absolute;left:-7px;top:-7px;color:var(--ink)}
.lchip{width:52px;height:52px;border-radius:50%;background:var(--c);color:var(--paper);border:3px solid var(--paper);font:700 40px/52px Khand;text-align:center}
.r7h{display:flex;align-items:center;gap:16px;height:76px;font:700 62px/1 Khand,Mukta;white-space:nowrap}.r7h #r7t{padding-top:8px}
.r7c{width:64px;height:64px;background:var(--blue);color:var(--paper);font:700 60px/66px Khand;text-align:center}
.r7l{display:flex;flex-wrap:wrap;align-items:center;gap:4px 20px;margin-top:6px;font:700 50px/1.2 Khand,Mukta;color:var(--c);white-space:nowrap}
.upa{display:inline-block;transform:rotate(-90deg);margin:0 -4px 0 -8px}
`;

export const html = stage({ html: H, css, part: 3 });
await cli({ html, part: 3, dur });
