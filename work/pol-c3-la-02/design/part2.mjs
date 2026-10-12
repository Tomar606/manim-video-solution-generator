// POL-C3-LA-02 part 2: अप्रैल 2006 -> 28 मई 2008 -> 2015. Drawing only, on the kit.
// Every time below is asked from the word clock by quoting what he says.
import { load, stage, cli, browser, cue, item, line, pips, heading, slip, stamp, text, box, wash, tiles, skeleton, crown, book, sym, arrow } from './kit.mjs';

const { S, at, scope, dur } = load(2);
const r1 = x => Math.round(x * 10) / 10;
// the line, large, in the lower part of the picture window (scenes with no shot)
const WIN = { x: 170, y: 700, w: 780, h: 200, yf: 52, row: 0, af: 40, tf: 46, sw: 11, r: 14, a: 1 };
// a ring that opens once on a point of the line ("here")
const PULSE = [];
const pulse = (k, t, c = 'blue') => PULSE.push({ u: line.u(k), t: +t.toFixed(3), c });
// an item in his zone right after a 'you' scene waits for him to finish gliding away
const late = (t, s) => Math.max(t, s.t0 + .28);
const T = {};          // times and geometry the browser code needs
let H = '', s;

// ---------------------------------------------------------------- s1 ----
// Part 1 in one breath: the line rewinds, then runs up at 1990 and down at 2002.
s = scope('s1');
line.start({ ink: '2002', pencil: 1, named: ['1990', '2002'], title: true, mode: 'mid' });
H += pips({ at: 0, out: null, filled: 2, fill: [null, null, at('s2', 'जन-आंदोलन'), at('s6', 'नेतृत्व'), at('s9', 'संविधान-सभा'), at('s12', 'राजशाही')] });
line.ink('start', s.at('Part 1'), .4, { cue: false });
line.ink('1990', s.at('पृष्ठभूमि'), .7);
line.ink('edge', s.at('1990'), 1.1); pulse('1990', s.at('1990'));
line.ink('2002', s.at('2002'), .7, { drop: true }); pulse('2002', s.at('2002') + .7, 'red');
{
  const pk = line.pt('peak', 'mid');
  H += text({ html: 'संविधान', ink: 'blue', size: 56, at: s.at('संविधान'), x: pk.x - 10, y: pk.y - 96 });
  H += text({ html: 'लोकतंत्र का खात्मा', ink: 'red', size: 52, at: s.at('लोकतंत्र'), x: 728, y: 588 });
}

// ---------------------------------------------------------------- s2 ----
s = scope('s2');
line.mode(s.t0, 'strip');
line.ink('floor', s.at('आता'), .8);
line.name('2006', s.at('2006')); pulse('2006', s.at('2006'));
wash('blue', s.at('जन-आंदोलन'), S.s5.t1);
item('y2b', { at: s.at('2006'), fx: 'press' });
H += heading({ id: 'h2', n: 3, year: 'अप्रैल <span id="y2b" class="sub">2006</span>', text: 'जन-आंदोलन', ink: 'blue', at: s.at('इसके बाद'), atYear: s.at('अप्रैल'), atText: s.at('जन-आंदोलन'), x: 70, y: 300 });
H += slip({ text: '= जनता का देशव्यापी आंदोलन', at: s.at('जनता'), x: 90, y: 690 });

// ---------------------------------------------------------------- s3 ----  V6
s = scope('s3');
pulse('2006', s.at('2006'));
H += text({ html: 'पूरे देश में', ink: 'ink', size: 72, at: s.at('पूरे'), x: 56, y: 1062 });
H += text({ html: 'लोकतंत्र-समर्थक प्रदर्शन', ink: 'blue', size: 72, at: s.at('लोकतंत्र-समर्थक'), x: 366, y: 1062, cue: 'stamp' });

// ---------------------------------------------------------------- s4 ----
// The line, large: it turns upward on "पहली बड़ी जीत"; the plate and its crown bow on "झुकना".
s = scope('s4');
line.mode(s.t0, WIN);
H += box(`${sym('people', { size: 64 })}<span>जनता</span>`, { at: s.at('जनता'), x: 70, y: 322, cls: 'chip blue', fx: 'slideL', cue: 'slide' });
H += box('<span>+ राजनीतिक ताकतें</span>', { at: s.at('राजनीतिक'), x: 70, y: 432, cls: 'chip blue', fx: 'slideL', cue: 'slide', style: 'font-size:60px' });
H += text({ html: 'पहली बड़ी जीत', ink: 'blue', size: 96, at: s.at('पहली'), x: 56, y: 1046, cue: 'stamp' });
line.ink('2006', s.at('पहली'), 1.0); pulse('2006', s.at('पहली') + 1.0);
T.bow = s.at('झुकना');
H += box(crown({ size: 96, id: 'c4' }), { at: s.at('राजा'), x: 846, y: 312, fx: 'slideR', cue: false });
H += box('<div id="k4" class="kplate">राजा ज्ञानेन्द्र</div>', { at: s.at('राजा'), x: 596, y: 402, fx: 'slideR', cue: 'slide' });
cue('slide', T.bow);

// ---------------------------------------------------------------- s5 ----  V7
s = scope('s5');
line.mode(s.t0, 'strip');
pulse('2002', s.at('2002'), 'red');
H += stamp({ text: 'भंग', ink: 'red', at: s.at('भंग'), x: 84, y: 1050, size: 80, rot: -5 });
item('k5', { at: s.at('फिर'), fx: 'draw', len: 250, d: .25 }); cue('scratch', s.at('फिर'), .25);
H += `<svg class="arw ink" width="1080" height="1920" fill="none" stroke="currentColor" stroke-width="13" stroke-linecap="round"><path id="k5" class="svi" d="M62 1158 L292 1060" stroke-dasharray="250" stroke-dashoffset="250"/></svg>`;
H += stamp({ text: 'संसद बहाल', ink: 'blue', at: s.at('बहाल'), x: 400, y: 1046, size: 84, rot: -3 });

// ---------------------------------------------------------------- s6 ----
s = scope('s6');
H += heading({ id: 'h6', n: 4, text: 'नेतृत्व और प्रतिरोध', ink: 'blue', at: s.at('अगला'), atText: s.at('नेतृत्व'), x: 70, y: 330 });

// ---------------------------------------------------------------- s7 ----  V8
s = scope('s7');
H += text({ html: 'ऐतिहासिक प्रतिरोध', ink: 'ink', size: 64, at: late(s.at('ऐतिहासिक'), s), x: 56, y: 1068 });
H += box('<span>अहिंसक</span>', { at: s.at('अहिंसक'), x: 560, y: 1046, cls: 'chip blue', fx: 'press', cue: 'stamp', style: 'font-size:92px' });
H += slip({ text: '= बिना हिंसा के', at: s.at('बिना'), x: 44, y: 1236 });

// ---------------------------------------------------------------- s8 ----
// नेतृत्व is the bar; three slots lock under it on "मिलकर"; then they fill 1/3, 2/3, 3/3.
s = scope('s8');
{
  const t = { bar: s.at('नेतृत्व'), slots: s.at('तीन'), lock: s.at('मिलकर'), a: s.at('सात'), b: s.at('माओवादी'), c: s.at('सामाजिक') };
  T.lock = t.lock;
  let cnt = '';
  [['0 / 3', t.slots, t.a], ['1 / 3', t.a, t.b], ['2 / 3', t.b, t.c], ['3 / 3', t.c, s.t1]].forEach(([lb, a, b], i) => {
    item(`c8_${i}`, { at: a, out: b, fx: 'none', hold: i < 3 }); cnt += `<span id="c8_${i}" class="sub">${lb}</span>`;
  });
  H += box(`<span>नेतृत्व</span><span class="cnt8">${cnt}</span>`, { at: t.bar, x: 110, y: 350, w: 860, cls: 'bar8', fx: 'slideD', cue: 'slide' });
  let marks = '';
  for (let k = 0; k < 7; k++) { item(`m7_${k}`, { at: t.a + .2 + k * .07, fx: 'pop' }); marks += `<i id="m7_${k}" class="sub mk7"></i>`; }
  H += tiles({ id: 'tl8', at: t.slots, x: 110, y: 472, w: 860, th: 140, gap: 30, size: 68, count: false, items: [
    { html: 'सात दलों का गठबंधन', at: t.a, ink: 'blue', sub: marks },
    { html: 'माओवादी समूह', at: t.b, ink: 'blue' },
    { html: 'सामाजिक कार्यकर्ता', at: t.c, ink: 'blue' } ] });
  H += box('', { at: t.lock + .22, x: 94, y: 334, w: 892, h: 568, cls: 'lock8', fx: 'press', cue: 'stamp' });
}

// ---------------------------------------------------------------- s9 ----
s = scope('s9');
{
  const lead = s.at('यही');
  H += stamp({ text: 'संसद बहाल', ink: 'blue', at: s.at('बहाल'), out: lead, x: 84, y: 306, size: 64, rot: -4 });
  H += text({ html: `अगला कदम ${arrow({ size: 64 })}`, ink: 'ink', size: 68, at: s.at('अगला'), out: lead, x: 90, y: 462 });
  H += text({ html: 'नया संविधान बनाना', ink: 'blue', size: 104, at: s.at('नया'), out: lead, x: 90, y: 552, cue: 'stamp' });
  line.ink('sabha', s.at('अगला'), 1.0);
  line.mark('sabha', s.at('संविधान-सभा')); pulse('sabha', s.at('संविधान-सभा'));
  H += heading({ id: 'h9', n: 5, text: 'संविधान-सभा का गठन', ink: 'blue', at: s.at('अगला', { nth: 2 }), atText: s.at('संविधान-सभा'), x: 70, y: 330 });
}

// --------------------------------------------------------------- s10 ----  V9
s = scope('s10');
pulse('sabha', late(s.at('संविधान-सभा'), s));
H += text({ html: 'संविधान-सभा', ink: 'blue', size: 76, at: late(s.at('संविधान-सभा'), s), x: 56, y: 1060, cue: 'stamp' });
item('s10b', { at: s.at('लिखना'), fx: 'fade' });
H += slip({ html: '= संविधान <span id="s10b" class="sub">लिखने वाली सभा</span>', at: s.at('संविधान'), x: 462, y: 1068, from: 'R' });
H += text({ html: 'नेपाल का', font: 'body', ink: 'ink', size: 46, at: s.at('नेपाल'), x: 50, y: 1212 });
H += text({ html: 'नया संविधान', ink: 'ink', size: 68, at: s.at('नया'), x: 50, y: 1268 });
H += arrow({ x1: 200, y1: 1364, x2: 200, y2: 1420, ink: 'ink', at: s.at('लिखने') });
item('s10c', { at: s.at('संविधान-सभा', { nth: 2 }), fx: 'press' }); item('s10d', { at: s.at('बनाई'), fx: 'pop' }); cue('tick', s.at('बनाई'));
H += box(`<div>विशेष <span id="s10d" class="sub">${sym('tick', { size: 54 })}</span></div><span id="s10c" class="sub">संविधान-सभा</span>`, { at: s.at('विशेष'), x: 50, y: 1436, cls: 'chip2 blue', fx: 'press', cue: 'stamp' });

// --------------------------------------------------------------- s11 ----
// The forked road: the red branch is left, the walker turns onto the blue one, which joins the line.
s = scope('s11');
{
  const bez = (a, b, c, d, n = 40) => Array.from({ length: n + 1 }, (_, i) => { const t = i / n, u = 1 - t; return [0, 1].map(k => u * u * u * a[k] + 3 * u * u * t * b[k] + 3 * u * t * t * c[k] + t * t * t * d[k]); });
  const poly = pts => { let L = 0; return pts.map((p, i) => { if (i) L += Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]); return [r1(p[0]), r1(p[1]), r1(L)]; }); };
  const F = [420, 790], J = line.pt('sabha', 'strip');
  const t = { trunk: s.at('इसी'), walker: s.at('माओवादी'), walk: s.at('समूहों'), red: s.at('हिंसा'), red2: s.at('सशस्त्र'), leave: s.at('छोड़कर'),
    blue: s.at('लोकतांत्रिक'), blue2: s.at('राजनीति'), go: s.at('में'), join: s.at('फैसला'), t1: s.t1 };
  T.road = { t, J, trunk: poly(bez([330, 1012], [330, 930], [400, 880], F, 16)), red: poly(bez(F, [435, 660], [240, 650], [190, 505])),
    blue: poly([...bez(F, [440, 640], [790, 640], [833, 470]), [833, 400], [833, 332]]) };
  cue('scratch', t.trunk, .5); cue('scratch', t.red, .5); cue('stamp', t.leave); cue('scratch', t.blue, .6); cue('slide', t.go); cue('tick', t.join + .4);
  pulse('sabha', t.join + .4);
  H += text({ html: 'माओवादी समूह', ink: 'ink', size: 60, at: t.walker, x: 455, y: 934 });
  H += text({ html: '<span id="rl1">हिंसा</span>', ink: 'red', size: 60, at: t.red, x: 70, y: 310 });
  H += text({ html: '<span id="rl2">सशस्त्र संघर्ष</span>', ink: 'red', size: 68, at: t.red2, x: 70, y: 376 });
  H += text({ html: 'लोकतांत्रिक', ink: 'blue', size: 68, at: t.blue, x: 600, y: 735 });
  H += text({ html: 'राजनीति', ink: 'blue', size: 68, at: t.blue2, x: 600, y: 815 });
}

// --------------------------------------------------------------- s12 ----
s = scope('s12');
item('f12b', { at: s.at('important'), fx: 'fade' });
H += box('सबसे <span id="f12b" class="sub">important</span>', { at: s.at('सबसे'), x: 0, y: 292, cls: 'flag', fx: 'slideL', cue: 'slide' });
H += heading({ id: 'h12', n: 6, ink: 'ink', at: s.at('point'), x: 70, y: 412 });
H += text({ html: 'राजशाही का अंत', ink: 'red', size: 104, at: s.at('राजशाही'), x: 252, y: 392, cue: 'stamp' });
H += text({ html: 'गणराज्य का उदय', ink: 'blue', size: 104, at: s.at('गणराज्य'), x: 252, y: 506, cue: 'stamp' });
H += slip({ text: 'ध्यान से सुनना', at: s.at('ध्यान'), x: 90, y: 676 });
H += text({ html: 'तारीख', ink: 'ink', size: 100, at: s.at('तारीख'), x: 560, y: 656 });
H += sym('cross', { at: s.at('गलत'), x: 800, y: 672, size: 88, ink: 'ink' }); cue('tick', s.at('गलत'));

// --------------------------------------------------------------- s13 ----
// THE DATE. He is hidden: the red 240-year bar runs out, then the page is stamped 28 मई 2008,
// and the stamp HOLDS, full size, to the cut. राजतंत्र arrives beside it and is struck on "खत्म".
s = scope('s13');
{
  const t = { n: s.at('नेपाल'), y: s.at('240'), v: s.at('वर्षों'), raj: s.at('राजशाही'), end: s.at('अंत'), d: s.at('28'), m: s.at('मई'), y8: s.at('2008'), t1: s.t1 };
  T.bar = { t0: t.y, t1: t.raj + .5, end: t.end, out: t.t1, x: 90, y: 612, w: 900, h: 96, n: 24 };
  wash('red', t.y, t.d + .4); wash('blue', t.d, dur);
  cue('scratch', t.y, T.bar.t1 - t.y); cue('stamp', t.end);
  H += text({ html: 'नेपाल', ink: 'ink', size: 110, at: t.n, x: 90, y: 296 });
  item('v13', { at: t.v, fx: 'press' });
  H += text({ html: '240 <span id="v13" class="sub">वर्ष</span>', ink: 'red', size: 150, at: t.y, x: 90, y: 426, cue: 'stamp' });
  item('a13', { at: t.end, fx: 'press' });
  H += text({ html: 'राजशाही <span id="a13" class="sub ink">का अंत</span>', ink: 'red', size: 96, at: t.raj, x: 90, y: 722 });
  item('dm13', { at: t.m, fx: 'slam' }); cue('stamp', t.m);
  item('dy13', { at: t.y8, fx: 'slam' }); cue('stamp', t.y8); cue('drop', t.y8);
  H += stamp({ id: 'dt13', html: '<span>28</span> <span id="dm13" class="sub">मई</span><br><span id="dy13" class="sub">2008</span>', ink: 'blue', at: t.d, x: 90, y: 892, w: 900, size: 284, rot: -3,
    style: 'line-height:.98;border-width:14px;outline-width:6px;outline-offset:10px;border-radius:26px;padding:56px 0 6px;text-align:center' });
  line.name('2008', t.y8); pulse('2008', t.y8);
  // राजतंत्र and its crown, top right, clear of the date; they stay through the cut and go on "गणराज्य" (s14)
  const k = { raj: s.at('राजतंत्र'), end: s.at('खत्म'), gone: at('s14', 'गणराज्य') };
  T.bow2 = k.end; T.fall = k.gone;
  H += box(crown({ size: 104, id: 'c14' }), { at: k.raj, out: k.gone + .6, x: 760, y: 316, fx: 'slideR', cue: false });
  H += box('<div class="kplate" style="font-size:96px">राजतंत्र</div>', { at: k.raj, out: k.gone + .75, x: 648, y: 414, fx: 'slideR', cue: 'slide' });
  item('k14', { at: k.end, out: k.gone + .75, fx: 'draw', len: 372, d: .25 }); cue('scratch', k.end, .25); cue('slide', k.end); cue('drop', k.gone + .45);
  H += `<svg class="arw ink" width="1080" height="1920" fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="round"><path id="k14" class="svi" d="M626 522 L990 446" stroke-dasharray="372" stroke-dashoffset="372"/></svg>`;
}

// --------------------------------------------------------------- s14 ----
// "एक लोकतांत्रिक गणराज्य बन गया": the line reaches the top and the crown tumbles off on "गणराज्य". The date stays, smaller.
s = scope('s14');
line.mode(s.t0, WIN);
{
  const t = { in: s.t0 + .15, rep: s.at('लोकतांत्रिक'), gan: s.at('गणराज्य'), ban: s.at('बन') };
  H += stamp({ text: '28 मई 2008', ink: 'blue', at: t.in, x: 70, y: 346, size: 76, rot: -3, cue: false, hold: true });   // no fade: it jumps to the band at the cut
  line.ink('2008', t.rep, t.gan - t.rep); pulse('2008', t.gan);
  item('b14a', { at: t.in, fx: 'press' }); item('b14b', { at: t.ban, fx: 'press' }); item('b14c', { at: t.rep, fx: 'press' }); item('b14d', { at: t.gan, fx: 'press' });
  cue('stamp', t.rep); cue('stamp', t.gan); cue('tick', t.ban);
  H += box('<span id="b14a" class="sub ink">नेपाल</span><span id="b14b" class="sub ink">बना</span><span id="b14c" class="sub blue">लोकतांत्रिक</span><span id="b14d" class="sub blue">गणराज्य</span>', { at: t.in, x: 56, y: 1056, cls: 'row14', fx: 'none' });
}

// --------------------------------------------------------------- s15 ----  V10
// Band: the term, and the date to memorise. Left column: who is the head of the country.
s = scope('s15');
line.mode(s.t0, 'strip');
H += stamp({ text: '28 मई 2008', ink: 'blue', at: s.t0, x: 610, y: 1056, size: 70, rot: -3, fx: 'fade', cue: false });
H += text({ html: 'गणराज्य', ink: 'blue', size: 92, at: s.at('गणराज्य'), x: 56, y: 1050, cue: 'stamp' });
item('p15', { at: s.at('प्रमुख'), fx: 'press' });
H += text({ html: 'देश का <span id="p15" class="sub">प्रमुख</span>', font: 'body', ink: 'ink', size: 48, at: s.at('देश'), x: 50, y: 1200 });
item('x15', { at: s.at('नहीं'), fx: 'pop' }); cue('tick', s.at('नहीं'));
H += slip({ html: `<b class="red">राजा</b> <span id="x15" class="sub">${sym('cross', { size: 46, ink: 'ink' })}</span>`, at: s.at('राजा'), x: 50, y: 1276, size: 60 });
H += box(arrow({ size: 60 }), { at: s.at('बल्कि'), x: 150, y: 1392, style: 'transform:rotate(90deg)', fx: 'fade' });
item('v15', { at: s.at('व्यक्ति'), fx: 'fade' }); item('k15', { at: s.at('व्यक्ति', { end: true }), fx: 'pop' }); cue('tick', s.at('व्यक्ति', { end: true }));
H += slip({ html: `<b class="blue">चुना हुआ<br><span id="v15" class="sub">व्यक्ति</span></b> <span id="k15" class="sub">${sym('tick', { size: 46, ink: 'blue' })}</span>`, at: s.at('चुना'), x: 50, y: 1450, size: 56 });

// --------------------------------------------------------------- s16 ----
s = scope('s16');
line.mode(s.t0, WIN);
line.name('2015', s.at('2015')); line.ink('2015', s.at('2015'), 1.0); pulse('2015', s.at('2015') + 1.0);
H += heading({ size: 'band', year: '2015', text: 'नया संविधान', ink: 'blue', at: s.at('2015'), atYear: s.at('2015'), atText: s.at('नया'), x: 56, y: 1054 });
H += box(book({ size: 150, ink: 'blue' }), { at: s.at('संविधान'), x: 790, y: 388, fx: 'pop', cue: 'flip' });
H += sym('tick', { at: s.at('अपनाया'), x: 912, y: 348, size: 84, ink: 'blue' }); cue('tick', s.at('अपनाया'));

// --------------------------------------------------------------- s17 ----
s = scope('s17');
line.mode(s.t0, 'strip');
H += skeleton({ id: 'sk17', at: [s.at('छहों'), s.at('छहों'), s.at('भारत')], done: [true, false, false], ticks: [null, s.at('पूरे'), null], arrow: { i: 2, at: s.at('लिखनी') }, x: 160, y: 286, w: 760 });
H += text({ html: `Part 3 ${arrow({ size: 84 })}`, ink: 'blue', size: 88, at: s.at('Part 3'), x: 160, y: 716, cue: 'stamp' });

T.pulse = PULSE;

// ------------------------------------------------------------------ CSS ----
const css = `
.chip{display:flex;align-items:center;gap:14px;background:var(--c);color:var(--paper);font:700 68px/1.2 Khand,Mukta;padding:8px 26px 2px;white-space:nowrap}
.chip .sy{color:var(--paper)}
.chip2{background:var(--c);color:var(--paper);font:700 64px/1.16 Khand,Mukta;padding:10px 24px 4px;white-space:nowrap}
.chip2 .sy{color:var(--paper);display:inline-block;vertical-align:-6px}
.kplate{background:var(--red);color:var(--paper);font:700 76px/1.15 Khand,Mukta;padding:10px 30px 4px;box-shadow:8px 8px 0 rgba(27,26,23,.2);white-space:nowrap;transform-origin:0 100%}
#c4,#c14{transform-origin:50% 92%}
.bar8{display:flex;justify-content:space-between;align-items:center;height:92px;background:var(--ink);color:var(--paper);font:700 72px/1 Khand,Mukta;padding:8px 30px 0}
.cnt8{position:relative;width:150px;height:72px}.cnt8 .sub{position:absolute;right:0;top:0;white-space:nowrap}
.mk7{width:24px;height:24px;margin:0 7px;background:var(--paper);border-radius:4px}
.lock8{border:9px solid var(--ink)}
.flag{background:var(--red);color:var(--paper);font:700 62px/1.2 Khand,Mukta;padding:8px 64px 0 70px;white-space:nowrap;clip-path:polygon(0 0,100% 0,calc(100% - 30px) 50%,100% 100%,0 100%)}
.row14{display:flex;gap:22px;align-items:baseline;font:700 80px/1.2 Khand,Mukta;white-space:nowrap}
.sl .sy{display:inline-block;vertical-align:-5px}
#sk17 .skp i{background:var(--blue);border-color:var(--blue)}#sk17 .skp i:nth-child(2){background:var(--red);border-color:var(--red)}
#bz{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;pointer-events:none}
`;
H += '<svg id="bz" viewBox="0 0 1080 1920" fill="none"><g id="bzG"></g></svg>';

// -------------------------------------------------------------- browser ----
// Bespoke drawing, each a pure function of t. Movement goes in steps (q), never as a glide.
const js = browser(function (T) {
  const q = (x, n) => Math.round(x * n) / n;
  const dOf = pts => pts.map((p, i) => (i ? 'L' : 'M') + p[0] + ' ' + p[1]).join('');
  const along = (pts, p) => { const L = pts[pts.length - 1][2] * clamp(p); let i = 1; while (i < pts.length - 1 && pts[i][2] < L) i++; const a = pts[i - 1], b = pts[i], k = b[2] > a[2] ? (L - a[2]) / (b[2] - a[2]) : 0; return [lerp(a[0], b[0], k), lerp(a[1], b[1], k), Math.atan2(b[1] - a[1], b[0] - a[0])]; };
  const road = (pts, col, p, o) => { const L = pts[pts.length - 1][2]; return p <= 0 ? '' : '<path d="' + dOf(pts) + '" stroke="' + col + '" stroke-width="46" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="' + f1(L + 60) + '" stroke-dashoffset="' + f1((L + 60) * (1 - p)) + '" opacity="' + f2(o) + '"/>' +
    (p >= 1 ? '<path d="' + dOf(pts) + '" stroke="' + COL.paper + '" stroke-width="5" stroke-dasharray="20 22" opacity="' + f2(o * .9) + '"/>' : ''); };

  function pulses(t) {
    let s = '';
    for (const p of T.pulse) {
      const k = q((t - p.t) / .5, 12); if (k <= 0 || k >= 1) continue;
      const pt = linePoint(p.u, t); if (!pt) continue;
      const r0 = pt.y < 260 ? 12 : 20;
      s += '<circle cx="' + f1(pt.x) + '" cy="' + f1(pt.y) + '" r="' + f1(r0 * (1 + 2.6 * eout(k))) + '" stroke="' + COL[p.c] + '" stroke-width="' + f1(r0 * .5 * (1 - k) + 2) + '" opacity="' + f2(1 - k * k) + '"/>';
    }
    return s;
  }

  // s11: the forked road
  function fork(t) {
    const R = T.road, c = R.t;
    if (t < c.trunk || t >= c.t1) return '';
    const o = 1 - P(t, c.t1 - .2, c.t1), left = q(P(t, c.leave, c.leave + .4), 5);
    let s = '<g opacity="' + f2(o) + '">';
    s += road(R.trunk, COL.ink, q(eout(P(t, c.trunk, c.trunk + .5)), 10), 1);
    s += road(R.red, COL.red, q(eout(P(t, c.red, c.red + .5)), 10), 1 - .76 * left);
    s += road(R.blue, COL.blue, q(eout(P(t, c.blue, c.blue + .6)), 12), 1);
    if (left > 0) {                                           // the red way is shut
      const b = along(R.red, .2), nx = Math.cos(b[2] + Math.PI / 2), ny = Math.sin(b[2] + Math.PI / 2), h = 56 * Math.min(1, left * 2.5);
      s += '<path d="M' + f1(b[0] - nx * h) + ' ' + f1(b[1] - ny * h) + 'L' + f1(b[0] + nx * h) + ' ' + f1(b[1] + ny * h) + '" stroke="' + COL.ink + '" stroke-width="18" stroke-linecap="round"/>';
    }
    // the blue way runs up into THE LINE
    const j = q(eout(P(t, c.join, c.join + .4)), 8);
    if (j > 0) {
      const y0 = 318, y1 = R.J.y + 16, y = lerp(y0, y1, j);
      s += '<path d="M' + R.J.x + ' ' + y0 + 'V' + f1(y) + '" stroke="' + COL.blue + '" stroke-width="9" stroke-linecap="round"/>' +
        '<path d="M' + (R.J.x - 17) + ' ' + f1(y + 22) + 'L' + R.J.x + ' ' + f1(y) + 'L' + (R.J.x + 17) + ' ' + f1(y + 22) + '" stroke="' + COL.blue + '" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>';
    }
    // the walker: up the trunk, waits at the fork, turns onto the blue way
    if (t >= c.walker) {
      const go = q(eio(P(t, c.go, c.join - .1)), 12), up = q(eio(P(t, c.walk, c.red - .15)), 8);
      const w = go > 0 ? along(R.blue, .04 + .96 * go) : along(R.trunk, .12 + .88 * up), col = go > 0 ? COL.blue : COL.ink, k = .4 + .6 * eback(P(t, c.walker, c.walker + .22));
      s += '<g transform="translate(' + f1(w[0]) + ' ' + f1(w[1]) + ') scale(' + f2(k) + ')"><circle r="34" fill="' + COL.paper + '" stroke="' + col + '" stroke-width="7"/><circle cy="-10" r="9" fill="' + col + '"/><path d="M-17 20 V12 Q-17 2 0 2 Q17 2 17 12 V20 Z" fill="' + col + '"/></g>';
    }
    $('rl1').style.opacity = $('rl2').style.opacity = f2(1 - .62 * left);
    return s + '</g>';
  }

  // s13: 240 years, a decade a block, and where they stop
  function bar(t) {
    const B = T.bar;
    if (t < B.t0 || t >= B.out) return '';
    const o = Math.min(P(t, B.t0, B.t0 + .15), 1 - P(t, B.out - .2, B.out)), n = Math.floor(B.n * P(t, B.t0, B.t1) + 1e-6), sw = B.w / B.n;
    let s = '<g opacity="' + f2(o) + '"><rect x="' + B.x + '" y="' + B.y + '" width="' + B.w + '" height="' + B.h + '" stroke="' + COL.ink + '" stroke-width="5"/>';
    for (let i = 0; i < n; i++) s += '<rect x="' + f1(B.x + i * sw + 3) + '" y="' + (B.y + 7) + '" width="' + f1(sw - 6) + '" height="' + (B.h - 14) + '" fill="' + COL.red + '"/>';
    const e = q(eout(P(t, B.end, B.end + .14)), 4);
    if (e > 0) s += '<rect x="' + (B.x + B.w + 8) + '" y="' + f1(B.y + B.h / 2 - 84 * e) + '" width="22" height="' + f1(168 * e) + '" fill="' + COL.ink + '"/>';
    return s + '</g>';
  }

  let drawn = '';
  window.frame = t => {
    const s = pulses(t) + fork(t) + bar(t);
    if (s !== drawn) { $('bzG').innerHTML = s; drawn = s; }
    // s4: he bows
    const b = eout(P(t, T.bow, T.bow + .3));
    $('c4').style.transform = 'translate(' + f1(16 * b) + 'px,' + f1(8 * b) + 'px) rotate(' + f1(27 * b) + 'deg)';
    $('k4').style.transform = 'rotate(' + f1(3.5 * b) + 'deg)';
    // s8: the three slots lock under the bar
    const k = eio(P(t, T.lock, T.lock + .3)), gr = $('tl8').querySelector('.tlg');
    gr.style.gap = f1(lerp(30, 8, k)) + 'px'; gr.style.marginTop = f1(lerp(0, -22, k)) + 'px';
    // s13: the crown tips on "खत्म"; s14: it tumbles off the page on "गणराज्य"
    const b2 = eout(P(t, T.bow2, T.bow2 + .3)), f = ein(P(t, T.fall, T.fall + .55));
    $('c14').style.transform = 'translate(' + f1(16 * b2 + 360 * f) + 'px,' + f1(8 * b2 + 220 * f) + 'px) rotate(' + f1(27 * b2 + 140 * f) + 'deg)';
  };
}, T);

await cli({ html: stage({ html: H, css, js, part: 2 }), part: 2, dur });
