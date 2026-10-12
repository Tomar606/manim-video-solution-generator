// POL-C3-LA-05 part 1: hook, question, परिचय, points 1 and 2. 16 scenes on the kit.
//
//   node work/pol-c3-la-05/design/part1.mjs            -> out/layers/p1/{under,mask,overlay}.mov
//   node work/pol-c3-la-05/design/part1.mjs --cues     -> out/cues_p1.json
//   node work/pol-c3-la-05/design/part1.mjs --sheet    -> out/stills/p1/sheet_p1.png
//   node work/pol-c3-la-05/design/part1.mjs --stills 12.5,75 [--full]
//
// Every time is asked of the word clock by quoting what he says (s.at('...')), scoped to the scene.
// Free zones: explain = the disc (y 260-1040) when no picture runs, the band y 1085-1195;
// you = y 170-800; hidden = everything above y 1680. Nothing below y 1680 (captions).
import path from 'node:path';
import { VIDEO, LOOK, load, stage, cli, browser, item, cue, table, strip, text, tag, band, pointCard, plaque, stamp, words, img, pin, icon, box, mapAnchors, SCATTER, disc } from './kit.mjs';

const { at, scope, dur } = load(1);
let H = '', s;
const E = disc('explain'), Y = disc('you');
const sub = (id, html, t, fx = 'drop', cls = '', style = '') => { item(id, { at: t, fx }); return `<span id="${id}" class="sub ${cls}" style="${style}">${html}</span>`; };

// ---- s1 · to you · MP Board कक्षा 12वीं के बच्चों!
s = scope('s1');
H += tag({ html: 'MP Board', size: 84, at: s.at('MP'), cx: true, y: 300 });
H += tag({ html: 'कक्षा 12वीं', size: 84, at: s.at('कक्षा'), cx: true, y: 430 });
H += tag({ html: 'राजनीति विज्ञान', kind: 'brass', size: 56, at: s.at('के बच्चों'), cx: true, y: 580 });

// ---- s2 · explaining · 100 people, 22 of them lit; then rows of five, one (and a bit) lit
s = scope('s2');
{
  const t22 = s.at('22'), th = s.at('हर'), cell = 52, x0 = E.cx - cell * 5, y0 = E.cy - cell * 5;
  let g = '';
  for (let i = 0; i < 100; i++) {
    const x = x0 + (i % 10) * cell + 5, y = y0 + Math.floor(i / 10) * cell + 4;
    g += `<div id="pp${i}" class="it" style="left:${x}px;top:${y}px">${icon('person', 42, 'rgba(246,238,220,.5)')}</div>`;
    item(`pp${i}`, { at: s.at('दुनिया') + .25 + i * .012, out: th, fx: 'pop' });
    if (i < 22) { g += `<div id="pl${i}" class="it" style="left:${x}px;top:${y}px">${icon('person', 42, 'var(--brass)', 'filter:drop-shadow(0 0 6px rgba(255,220,120,.8))')}</div>`; item(`pl${i}`, { at: t22 + i * .03, out: th, fx: 'pop' }); }
  }
  cue('pluck', t22); cue('pluck', t22 + .33);
  H += g;
  // rows of five: one lit, and a sliver of the next
  let r = '';
  for (let i = 0; i < 5; i++) {
    const x = E.cx - 290 + i * 116;
    r += `<div id="pf${i}" class="it" style="left:${x}px;top:${E.cy - 80}px">${icon('person', 112, 'rgba(246,238,220,.55)')}</div>`;
    item(`pf${i}`, { at: th + i * .06, fx: 'pop' });
  }
  r += `<div id="pfl0" class="it" style="left:${E.cx - 290}px;top:${E.cy - 80}px">${icon('person', 112, 'var(--brass)')}</div>`;
  r += `<div id="pfl1" class="it" style="left:${E.cx - 290 + 116}px;top:${E.cy - 80}px;clip-path:inset(0 72% 0 0)">${icon('person', 112, 'var(--brass)')}</div>`;
  item('pfl0', { at: s.at('एक से'), fx: 'pop' }); item('pfl1', { at: s.at('ज़्यादा'), fx: 'fade', d: .3 });
  cue('pluck', s.at('एक से'));
  H += r;
  H += band({ html: 'दुनिया की जनसंख्या का <b style="color:var(--maroon)">22%</b>', at: t22, out: th });
  H += band({ html: 'हर 5 में से 1 से ज़्यादा इंसान', at: th });
}

// ---- s3 · explaining · V1 the crowd; then the region inlaid in the disc
s = scope('s3');
H += band({ html: 'सार्क के देशों में', at: s.at('सार्क'), out: s.at('तो इतने') });
table.mapDisc(s.at('तो इतने') - .1, s.t1);
H += band({ html: 'इतना बड़ा क्षेत्र', at: s.at('इतने'), out: s.at('योगदान') });
H += band({ html: 'विकास में सार्क का <b style="color:var(--maroon)">योगदान?</b>', at: s.at('योगदान') });

// ---- s4 · to you · the question card, stamp Board Exam 2024
s = scope('s4');
H += stamp({ text: 'Board Exam 2024', size: 70, at: s.at('board'), x: 30, y: 96, rot: -8, hold: true, style: 'z-index:2' });
H += img({ file: path.join(VIDEO, 'assets/question_sheet.png'), at: s.at('सवाल'), x: 175, y: 70, w: 730, h: 759, d: .2, hold: true });

// ---- s5 · explaining · the answer's shape: परिचय, then five points
s = scope('s5');
H += tag({ html: 'परिचय', size: 88, at: s.at('परिचय'), cx: true, y: 400 });
{
  const tf = s.at('पाँच');
  let r = '';
  for (let i = 0; i < 5; i++) r += `<div class="ss" style="position:absolute;left:${E.cx - 300 + i * 124}px;top:0;width:104px;height:104px;display:flex;align-items:center;justify-content:center"><b style="font:400 56px/1 Yatra;color:var(--cream);margin-top:8px">${i + 1}</b></div>`;
  H += box(r, { at: tf, x: 0, y: 580, w: 1080, h: 110, fx: 'slideU', cue: 'slide' });
  H += tag({ html: '5 points', size: 64, at: s.at('points'), cx: true, y: 730, kind: 'brass' });
}


// ---- s6 · explaining · सार्क = दक्षिण एशियाई क्षेत्रीय सहयोग संगठन
s = scope('s6');
H += plaque({ text: 'सार्क', size: 130, at: s.at('सार्क'), cx: true, y: 300 });
H += words({ items: [{ html: 'दक्षिण एशियाई', at: s.at('दक्षिण') }, { html: 'क्षेत्रीय', at: s.at('क्षेत्रीय') }, { html: 'सहयोग', at: s.at('सहयोग') }, { html: 'संगठन', at: s.at('संगठन') }],
  x: 0, w: 1080, y: 520, size: 58, gap: 14 });

// ---- s7 · explaining · जनसंख्या की दृष्टि से विश्व का सबसे बड़ा क्षेत्रीय संगठन · 22%
s = scope('s7');
H += tag({ html: 'जनसंख्या की दृष्टि से', size: 56, at: s.at('जनसंख्या'), cx: true, y: 330 });
H += box(`<div class="medal"><small>विश्व का</small>सबसे बड़ा</div>`, { at: s.at('सबसे'), cx: true, y: 440, fx: 'pop', cue: 'chime' });
H += tag({ html: 'क्षेत्रीय संगठन', size: 60, at: s.at('क्षेत्रीय'), cx: true, y: 830 });
H += band({ html: 'दुनिया की जनसंख्या का <b style="color:var(--maroon)">22%</b>', at: s.at('22') });

// ---- s8 · hidden · the eight members on the inlaid map
s = scope('s8');
table.mapFull(s.t0, s.t1);
{
  const M = mapAnchors().anchors;
  const P = [['afghanistan', 'अफ़ग़ानिस्तान', 'u'], ['bangladesh', 'बांग्लादेश', 'd'], ['bhutan', 'भूटान', 'u'], ['india', 'भारत', 'r'],
    ['nepal', 'नेपाल', 'u'], ['maldives', 'मालदीव', 'l'], ['pakistan', 'पाकिस्तान', 'd'], ['srilanka', 'श्रीलंका', 'r']];
  const ts = P.map(([, name]) => s.at(name));
  P.forEach(([k, name, side], i) => { H += pin({ x: M[k][0], y: M[k][1], name, side, at: ts[i] }); });
  H += tag({ html: 'सार्क के सदस्य देश', size: 60, at: s.at('सदस्य'), x: 60, y: 92 });
  let c = '';
  ts.forEach((t, i) => { item(`cnt${i}`, { at: t, out: i < 7 ? ts[i + 1] : undefined, fx: i ? 'none' : 'pop', hold: i < 7 }); c += `<b id="cnt${i}" class="sub" style="position:absolute;right:0;top:0">${i + 1}</b>`; });
  H += box(c, { at: ts[0], x: 840, y: 64, w: 180, h: 170, cls: 'counter', fx: 'pop' });
  H += tag({ html: 'कुल 8 देश', kind: 'brass', size: 84, at: s.at('कुल'), cx: true, y: 1500 });
}

// ---- s9 · to you · point 1
s = scope('s9');
H += pointCard({ n: 1, text: 'क्षेत्रीय सहयोग की शुरुआत', at: s.at('पहला'), atText: s.at('क्षेत्रीय'), y: 236 });

// ---- s10 · explaining · 1985, एक मंच, नींव: सहयोग · शांति · सामूहिक विकास
s = scope('s10');
H += stamp({ text: 'स्थापना 1985', size: 80, at: s.at('1985'), cx: true, y: 380, rot: -6 });
H += tag({ html: 'एक मंच', size: 96, kind: 'brass', at: s.at('एक मंच'), cx: true, y: 560 });
table.glow(s.at('एक मंच'), s.t1);
H += tag({ html: 'नींव', size: 64, kind: 'dark', at: s.at('नींव'), cx: true, y: 760 });
H += words({ items: [{ html: 'सहयोग', at: s.at('सहयोग') }, { html: 'शांति', at: s.at('शांति') }, { html: 'सामूहिक विकास', at: s.at('सामूहिक') }],
  row: true, x: 0, w: 1080, y: LOOK.band.y0 + 4, size: 60, gap: 20, kind: 'brass', style: 'justify-content:center' });

// ---- s11 · explaining · scattered, each with its own trouble; then round the table; V2
s = scope('s11');
{
  const ta = s.at('अलग-अलग'), tc = s.at('समस्याओं'), tb = s.at('साथ');
  table.seat(tb, tb + .9, ta);
  SCATTER.forEach(([dx, dy], i) => {
    H += box(icon('cloud', 96, '#c9ced8', 'filter:drop-shadow(0 0 2px #2b1d14) drop-shadow(0 4px 6px rgba(0,0,0,.5))'), { at: tc + i * .05, out: tb, x: E.cx + dx * E.r - 48, y: E.cy + dy * E.r - 112, fx: 'pop', cue: i ? false : 'pluck' });
  });
  H += band({ html: 'पहले: अलग-अलग', at: ta, out: tb });
  H += band({ html: 'अब: साथ बैठकर बात', at: tb, kind: 'brass' });
}

// ---- s12 · explaining · one problem, the same at every seat
s = scope('s12');
H += tag({ html: 'समस्या', size: 96, kind: 'coral', at: s.at('समस्या'), cx: true, y: 590 });
{
  const te = s.at('एक जैसी');
  for (let i = 0; i < 8; i++) {
    const a = -Math.PI / 2 + i * Math.PI / 4 + Math.PI / 8, rr = E.r - 46;
    H += box('<b class="qd">?</b>', { at: te + i * .04, x: E.cx + rr * Math.cos(a) - 30, y: E.cy + rr * Math.sin(a) - 30, fx: 'pop', cue: i ? false : 'knock' });
  }
  H += band({ html: 'सभी देशों में एक जैसी', at: s.at('सभी') });
}

// ---- s13 · to you · point 2
s = scope('s13');
table.turn(s.at('अगला'));
H += pointCard({ n: 2, text: 'गरीबी और बेरोज़गारी से मुकाबला', at: s.at('अगला'), atText: s.at('गरीबी'), y: 236 });

// ---- s14 · explaining · V3; गरीबी · भुखमरी · बेरोज़गारी, struck out together
s = scope('s14');
H += tag({ html: 'मुख्य उद्देश्य', kind: 'dark', size: 52, at: s.at('मुख्य'), cx: true, y: 945 });
H += words({ items: [{ html: 'गरीबी', at: s.at('गरीबी') }, { html: 'भुखमरी', at: s.at('भुखमरी') }, { html: 'बेरोज़गारी', at: s.at('बेरोजगारी') }],
  row: true, x: 0, w: 1080, y: LOOK.band.y0 + 4, size: 62, gap: 24, style: 'justify-content:center' });
{
  const tm = s.at('मिलकर'), len = 900;
  item('strike1', { at: tm, fx: 'draw', len, d: .35 }); cue('slide', tm, .35);
  H += `<svg class="arw" width="1080" height="1920"><path id="strike1" class="svi" d="M90 ${LOOK.band.y0 + 58} L990 ${LOOK.band.y0 + 46}" stroke="var(--coral)" stroke-width="14" stroke-linecap="round" stroke-dasharray="${len}" stroke-dashoffset="${len}"/></svg>`;
  H += tag({ html: 'मिलकर खत्म', kind: 'coral', size: 60, at: s.at('खत्म'), x: 640, y: 1000, rot: -4 });
}

// ---- s15 · explaining · V4; जीवनस्तर सुधरे
s = scope('s15');
H += band({ html: `आम लोगों का जीवनस्तर ${icon('up', 58, 'var(--teal)', 'vertical-align:-8px')}`, at: s.at('आम') });
H += tag({ html: 'सुधर सके', kind: 'teal', size: 56, at: s.at('सुधर'), x: 680, y: 960, rot: -4 });

// ---- s16 · to you · two done; the three still to come, in his words; Part 2
s = scope('s16');
H += tag({ html: '2 points हो गए', size: 64, at: s.at('दो'), cx: true, y: 214, kind: 'brass' });
H += words({ items: [{ html: '<i class="wn">3</i> व्यापार', at: s.at('व्यापार') }, { html: '<i class="wn">4</i> शिक्षा-स्वास्थ्य', at: s.at('शिक्षा-स्वास्थ्य') }, { html: '<i class="wn">5</i> रुकावटें', at: s.at('रुकावटें') }],
  x: 0, w: 1080, y: 330, size: 58, gap: 14 });
H += tag({ html: 'Part 2 में →', kind: 'coral', size: 66, at: s.at('Part'), cx: true, y: 650 });

// ---- the strip: from "तो पहले परिचय से" to the end; each point's card lands in its slot as the next scene starts
H += strip({ at: at('s5', 'तो पहले'), intro: at('s5', 'तो पहले'), fill: [scope('s10').t0, scope('s14').t0, null, null, null],
  now: [[at('s5', 'तो पहले'), 'p'], [at('s9', 'पहला'), 0], [at('s13', 'अगला'), 1], [at('s16', 'तो दो'), 'off']] });

const css = `
.medal{width:330px;height:330px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;font:800 76px/1 Baloo,Hind;color:#3a2410;
 background:radial-gradient(circle at 40% 35%,#f6dc8c,#d9a841 60%,#a67a22);box-shadow:0 0 0 10px #8a6218,0 0 0 22px rgba(217,168,65,.5),0 16px 28px rgba(20,8,2,.5);text-align:center;padding-top:10px}
.medal small{font:700 44px/1.2 Hind;display:block;margin-bottom:6px}
.counter b{font:400 170px/1 Yatra,Baloo;color:var(--brass);-webkit-text-stroke:6px #3a2410;paint-order:stroke fill}
.qd{display:flex;width:60px;height:60px;border-radius:50%;background:var(--coral);color:#fff7ee;font:800 46px/66px Baloo;justify-content:center;box-shadow:0 4px 8px rgba(0,0,0,.45)}
.wn{font:400 48px/1 Yatra;font-style:normal;color:#9c701c;margin-right:12px}
`;
await cli({ html: stage({ html: H, css, part: 1 }), part: 1, dur });
