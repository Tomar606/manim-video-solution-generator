// POL-C3-LA-02 part 1: hook, question, पृष्ठभूमि, 1990, 2002. 17 scenes on the kit.
//
//   node work/pol-c3-la-02/design/part1.mjs            -> out/layers/p1/{under,mask,overlay}.mov
//   node work/pol-c3-la-02/design/part1.mjs --cues     -> out/cues_p1.json
//   node work/pol-c3-la-02/design/part1.mjs --sheet    -> out/stills/p1/sheet_p1.png
//   node work/pol-c3-la-02/design/part1.mjs --stills 12.5,75 [--full]
//
// Every time is asked of the word clock by quoting what he says (s.at('...')), scoped to the scene.
// Only layout is decided here. Free zones per presenter state: look.json "place".
import path from 'node:path';
import { VIDEO, load, stage, cli, browser, line, strip, lineFull, item, cue, pips, heading, slip, stamp, text, box, wash, skeleton, crown, book, img, arrow } from './kit.mjs';

const { S, at, scope, dur } = load(1);
const T = {};            // times the browser code below needs
let H = '', s;

// words that land one after another on one row (band y 1040-1175)
const seq = (id, parts, o) => box(parts.map((p, i) => {
  item(`${id}_${i}`, { at: p.at, fx: 'press' }); cue('stamp', p.at);
  return `<span id="${id}_${i}" class="sub ${p.ink || 'ink'}" style="color:var(--c);margin-right:.24em">${p.html}</span>`;
}).join(''), { x: 50, y: 1058, ...o, id, at: Math.min(...parts.map(p => p.at)), fx: 'none', style: `font:700 ${o.size || 80}px/1.2 Khand,Mukta;white-space:nowrap` });
const sub = (id, html, t, cls = '', style = '') => { item(id, { at: t, fx: 'fade' }); return `<span id="${id}" class="sub ${cls}" style="${style}">${html}</span>`; };

line.start({ mode: 'off' });

// ---- s1 · to you · MP Board कक्षा 12वीं के बच्चों!
s = scope('s1');
H += text({ html: 'MP Board', size: 170, at: s.at('MP'), cx: true, y: 300 });
H += text({ html: 'कक्षा 12वीं', size: 170, at: s.at('कक्षा'), cx: true, y: 490 });
H += slip({ text: 'राजनीति विज्ञान', size: 52, at: s.at('के बच्चों'), cx: true, y: 706 });

// ---- s2 · explaining · V1 red · नेपाल, a bar that fills: 240 साल, राजशाही = राजा का शासन
s = scope('s2');
H += text({ html: 'नेपाल', size: 170, at: s.at('नेपाल'), cx: true, y: 66 });
T.bar = [s.at('240'), s.at('राजशाही') + .35];
{
  const a = s.at('240'), b = s.at('राजशाही');
  H += box(sub('b1r', '240 साल', a, 'blab', 'left:28px;color:var(--red)') + sub('b2r', 'राजशाही', b, 'blab', 'right:28px;color:var(--red)') +
    `<div id="bfill"><div class="bin">${sub('b1c', '240 साल', a, 'blab', 'left:28px') + sub('b2c', 'राजशाही', b, 'blab', 'right:28px')}</div></div>`,
    { at: s.at('लगभग'), x: 60, y: 1056, w: 960, h: 104, cls: 'bar240', fx: 'slideL', cue: 'slide' });
  cue('scratch', T.bar[0], T.bar[1] - T.bar[0]);
}
H += slip({ html: 'राजशाही =<br><b class="red">राजा का शासन</b>', at: s.at('राजा'), x: 50, y: 1250 });

// ---- s3 · explaining · the red card flips to blue, 2008 on the hinge, कैसे?
s = scope('s3');
T.flip = s.at('लोकतांत्रिक');
H += text({ html: '2008', size: 150, at: s.at('2008'), cx: true, y: 276 });
H += box('<i class="hinge"></i><div id="fc_r" class="face red">राजशाही</div><div id="fc_b" class="face blue">लोकतांत्रिक<br>गणराज्य</div>',
  { at: s.t0 + .15, x: 160, y: 470, w: 760, h: 290, fx: 'slideR', cue: 'slide' });
cue('flip', T.flip);
H += text({ html: 'कैसे?', size: 190, at: s.at('कैसे'), cx: true, y: 806, fx: 'slam', cue: 'stamp' });

// ---- s4 · to you · the question card, stamp Board Exam 2025
s = scope('s4');
H += text({ html: 'सिर्फ कहानी नहीं', size: 120, at: s.at('सिर्फ'), out: s.at('सवाल'), cx: true, y: 420 });
H += img({ file: path.join(VIDEO, 'assets/question_sheet.png'), at: s.at('सवाल'), x: 190, y: 72, w: 700, h: 727, fx: 'slideD', d: .15, hold: true, cue: 'slide' });   // a photograph: every frame it is on costs 0.7 MB, so it moves briefly and cuts out
H += stamp({ text: 'Board Exam 2025', size: 72, at: s.at('Board'), x: 56, y: 150, hold: true });
{
  const u = (id, x1, y1, x2, t) => { const len = x2 - x1 + 4; item(id, { at: t, fx: 'draw', len, d: .1, hold: true }); cue('scratch', t, .3); return `<path id="${id}" class="svi" d="M${x1} ${y1} L${x2} ${y1 - 7}" stroke-dasharray="${len}" stroke-dashoffset="${len}"/>`; };
  H += `<svg class="arw blue" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" opacity=".85">${u('qu1', 384, 599, 708, s.at('नेपाल')) + u('qu2', 382, 664, 590, s.at('स्थापित')) + u('qu3', 380, 727, 730, s.at('विस्तारपूर्वक'))}</svg>`;
}

// ---- s5 · explaining · the answer's three slots
s = scope('s5');
H += text({ html: 'इस answer में', size: 92, at: s.at('answer'), cx: true, y: 312 });
H += skeleton({ at: [s.at('पृष्ठभूमि'), s.at('छह'), s.at('भारत')], x: 160, y: 462, w: 760 });

// ---- s6 · hidden · THE LINE appears, full page: 1990 at one end, 2015 at the other
s = scope('s6');
lineFull(s.t0);
line.pencil(1, s.at('साल'), s.at('1990') - s.at('साल'));
line.name('1990', s.at('1990')).name('2015', s.at('2015'));
H += text({ html: 'points साल के क्रम में', size: 96, at: s.at('points'), cx: true, y: 250 });
H += text({ html: 'साल याद रहे', size: 104, at: s.at('साल', { nth: 2 }), cx: true, y: 1296 });
H += text({ html: 'तो points अपने आप याद', size: 84, at: s.at('points', { nth: 2 }), cx: true, y: 1436 });

// ---- s7 · explaining · V2 red · पृष्ठभूमि: अतीत हिंदू-राज्य, आधुनिक काल संवैधानिक राजतंत्र
s = scope('s7');
strip(s.t0);
H += pips({ at: s.t0 + .25, out: null, fill: [at('s11', 'पहला'), at('s14', 'अगला')] });
H += heading({ text: 'पृष्ठभूमि', size: 'band', at: s.at('पृष्ठभूमि'), out: S.s8.t1, x: 56, y: 1054 });
line.ink(.11, s.at('पृष्ठभूमि'), 1.2);
H += text({ html: 'अतीत', font: 'body', size: 44, at: s.at('अतीत'), x: 52, y: 1206 });
H += text({ html: 'हिंदू-राज्य', size: 84, ink: 'red', at: s.at('हिंदू-राज्य'), x: 50, y: 1256 });
H += text({ html: 'आधुनिक काल', font: 'body', size: 44, at: s.at('आधुनिक'), x: 52, y: 1392 });
H += text({ html: 'संवैधानिक', size: 76, ink: 'red', at: s.at('संवैधानिक'), x: 50, y: 1444 });
H += text({ html: 'राजतंत्र', size: 76, ink: 'red', at: s.at('राजतंत्र'), x: 50, y: 1528 });

// ---- s8 · explaining · a crown above a book
s = scope('s8');
H += text({ html: 'संवैधानिक राजतंत्र', size: 104, at: s.at('संवैधानिक'), cx: true, y: 312 });
H += crown({ size: 210, at: s.at('प्रमुख'), x: 120, y: 480 });
H += slip({ html: 'प्रमुख = <b class="red">राजा</b>', size: 62, at: s.at('राजा'), x: 400, y: 540, from: 'R' });
H += book({ size: 210, at: s.at('शासन'), x: 120, y: 760 });
H += slip({ html: 'शासन = संविधान के अनुसार', size: 46, at: s.at('संविधान'), x: 376, y: 830, from: 'R' });

// ---- s9 · explaining · V3 blue · the people's demand
s = scope('s9');
H += text({ html: 'राजनीतिक दल', size: 64, ink: 'blue', at: s.at('राजनीतिक'), x: 50, y: 1212 });
H += text({ html: '+ आम जनता', size: 64, ink: 'blue', at: s.at('आम'), x: 50, y: 1292 });
H += seq('dm', [{ html: 'खुले और उत्तरदायी शासन', at: s.at('खुले'), ink: 'blue' }, { html: 'की माँग', at: s.at('माँग'), ink: 'blue' }], {});
H += slip({ html: `= जनता के प्रति<br>${sub('jw', 'जवाबदेह', s.at('जवाबदेह'), 'blue', 'color:var(--c)')}`, at: s.at('जनता', { nth: 2 }), x: 50, y: 1436 });

// ---- s10 · explaining · the powers slide under the crown and turn red; the राह gets its name and stops
s = scope('s10');
H += crown({ size: 230, at: s.at('राजा'), x: 425, y: 312 });
H += slip({ text: 'सेना की मदद से', at: s.at('सेना'), x: 676, y: 420, from: 'R' });
T.pw = { go: s.at('अपने'), from: [0, 1, 2, 3].map(i => [75 + i * 240, 880]), to: [[325, 566], [545, 566], [325, 678], [545, 678]] };
H += box([0, 1, 2, 3].map(i => { item(`pw${i}`, { at: s.at('शक्तियाँ') + i * .08, fx: 'pop' }); cue('slide', T.pw.go + i * .3); return `<span id="pw${i}" class="sub pw" style="left:${T.pw.from[i][0]}px;top:880px">शक्ति</span>`; }).join(''),
  { at: s.at('शक्तियाँ'), x: 0, y: 0, w: 1080, h: 1030, fx: 'none' });
H += seq('pwb', [{ html: 'सारी शक्तियाँ', at: s.at('सारी') }, { html: 'अपने हाथों में', at: s.at('अपने'), ink: 'red' }], {});
wash('red', s.at('समेट'), s.t1);
line.title(s.at('लोकतंत्र'));
line.stop(s.at('रुक'), at('s11', 'पहला'));

// ---- s11 · to you · point 1
s = scope('s11');
H += heading({ n: 1, year: '1990', text: 'लोकतांत्रिक संविधान', ink: 'blue', at: s.at('पहला'), atYear: s.at('1990'), atText: s.at('लोकतांत्रिक'), x: 70, y: 320 });
line.ink('1990', s.at('1990'), .3);

// ---- s12 · explaining · V3, V4 blue · the king gives way; the line climbs
s = scope('s12');
H += seq('ad', [{ html: 'लोकतंत्र-समर्थक आंदोलन', at: s.at('लोकतंत्र-समर्थक'), ink: 'blue' }, { html: 'का दबाव', at: s.at('दबाव'), ink: 'blue' }], {});
H += box(arrow({ size: 64 }), { at: s.at('राजा'), x: 60, y: 1192, rot: 90, fx: 'fade' });
H += text({ html: 'राजा को', size: 72, ink: 'red', at: s.at('राजा'), x: 50, y: 1240 });
H += text({ html: 'माँग माननी पड़ी', size: 60, at: s.at('माँग'), x: 50, y: 1332 });
line.ink('peak', s.at('1990'), 1.5);

// ---- s13 · explaining · the governments tip over one after another; the line wobbles
s = scope('s13');
T.gov = { fall: s.at('कार्यकाल'), ang: [64, 64, 64, 64, 90] };
H += text({ html: 'लोकतांत्रिक सरकारें', size: 92, ink: 'blue', at: s.at('लोकतांत्रिक'), cx: true, y: 312 });
H += box([0, 1, 2, 3, 4].map(i => { item(`gv${i}`, { at: s.at('सरकारें') + i * .09, fx: 'pop' }); cue('tick', s.at('सरकारें') + i * .09); cue('flip', T.gov.fall + i * .42); return `<span id="gv${i}" class="sub gv" style="left:${60 + i * 160}px"><i id="gvi${i}">सरकार</i></span>`; }).join(''),
  { at: s.at('सरकारें'), x: 0, y: 470, w: 1080, h: 230, fx: 'none' });
H += text({ html: 'कार्यकाल छोटा', size: 92, at: s.at('कार्यकाल'), x: 90, y: 752 });
H += text({ html: 'राजनीतिक अस्थिरता', size: 92, at: s.at('राजनीतिक'), x: 90, y: 862 });
H += seq('pb', [{ html: 'समस्याओं से भरी', at: s.at('समस्याओं') }], {});
line.ink('edge', T.gov.fall, 5 * .42);          // the line moves on while they fall, so the two share their frames
line.wobble(s.at('अस्थिरता'), s.t1 - .2);

// ---- s14 · to you · point 2; the page turns red
s = scope('s14');
H += heading({ n: 2, year: '2002', text: 'लोकतंत्र का खात्मा', ink: 'red', at: s.at('अगला'), atText: s.at('लोकतंत्र'), atYear: s.at('2002'), x: 70, y: 320 });
H += slip({ html: '<b class="red">राजा</b> द्वारा', size: 56, at: s.at('राजा'), x: 664, y: 352, from: 'R' });
wash('red', s.at('राजा'), at('s17', 'वापस') - .2);
line.name('2002', s.at('2002'));

// ---- s15 · explaining · V5 red · parliament shut, the government thrown out
s = scope('s15');
H += stamp({ text: 'संसद भंग', ink: 'red', size: 76, at: s.at('भंग'), x: 64, y: 1050 });
H += slip({ text: '= निष्क्रिय', at: s.at('निष्क्रिय'), x: 480, y: 1076, from: 'R' });
H += text({ html: 'चुनी हुई सरकार', size: 60, ink: 'blue', at: s.at('चुनी'), x: 50, y: 1226 });
H += stamp({ text: 'सरकार बेदखल', ink: 'red', size: 54, at: s.at('बेदखल'), x: 48, y: 1340 });

// ---- s16 · hidden · the line drops to the floor
s = scope('s16');
lineFull(s.t0);
H += text({ html: 'थोड़ा-बहुत लोकतंत्र', size: 64, ink: 'blue', at: s.at('थोड़ा-बहुत'), out: s.at('समाप्त'), x: 322, y: 508 });
H += crown({ size: 120, at: s.at('राजा'), x: 486, y: 604 });
line.ink('2002', s.at('पूरी'), s.at('समाप्त') - s.at('पूरी') + .05, { drop: true });
H += stamp({ text: 'लोकतंत्र समाप्त', ink: 'red', size: 110, at: s.at('समाप्त') + .08, cx: true, y: 1310 });

// ---- s17 · to you · the cliffhanger: flat at 2002, a dotted path and "?" ahead
s = scope('s17');
const CLIFF = { x: 200, y: 330, w: 740, h: 150, yf: 50, row: 0, af: 40, tf: 44, sw: 10, r: 13, a: 1 };
line.mode(s.t0, CLIFF);
H += text({ html: 'लोकतंत्र खत्म', size: 104, ink: 'red', at: s.at('खत्म'), out: s.at('वापस') - .05, cx: true, y: 588 });
H += text({ html: 'वापस कैसे आया?', size: 104, at: s.at('वापस'), out: null, cx: true, y: 588 });
{ const q = line.pt('floor', CLIFF); H += text({ html: '?', size: 120, at: s.at('कैसे'), out: null, x: q.x - 62, y: q.y - 150, fx: 'pop', cue: 'tick' }); }
H += stamp({ html: `Part 2 ${arrow({ size: 56 })}`, size: 58, at: s.at('Part 2'), out: null, cx: true, y: 712 });

const css = `
.bar240{border:4px solid var(--ink);background:var(--slip);overflow:hidden}
.blab{position:absolute;top:4px;font:700 78px/96px Khand,Mukta;white-space:nowrap;color:var(--paper)}
#bfill{position:absolute;left:0;top:0;bottom:0;width:0;background:var(--red);overflow:hidden}
.bin{position:absolute;left:0;top:0;width:952px;height:96px}
.hinge{position:absolute;left:50%;top:-22px;bottom:-22px;width:8px;margin-left:-4px;background:var(--ink)}
.face{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;padding-top:10px;box-sizing:border-box;background:var(--c);color:var(--paper);font:700 150px/1 Khand,Mukta}
#fc_b{font-size:104px;line-height:1.12;display:none}
.pw{position:absolute;width:210px;height:96px;box-sizing:border-box;padding-top:6px;background:var(--blue);color:var(--paper);font:700 60px/90px Khand,Mukta;text-align:center}
.gv{position:absolute;top:0;width:150px;height:200px}
.gv i{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding-top:6px;box-sizing:border-box;background:var(--blue);color:var(--paper);font:normal 700 50px/1 Khand,Mukta;transform-origin:100% 100%}
`;

const js = browser(function (T) {
  window.frame = t => {
    // s2: the 240-year bar fills
    $('bfill').style.width = f1(952 * eio(P(t, T.bar[0], T.bar[1]))) + 'px';
    // s3: the card turns over on its hinge
    const e = eio(P(t, T.flip, T.flip + .5));
    $('fc_r').style.display = e < .5 ? 'flex' : 'none'; $('fc_b').style.display = e < .5 ? 'none' : 'flex';
    $('fc_r').style.transform = 'scaleX(' + f3(Math.max(.02, 1 - 2 * e)) + ')'; $('fc_b').style.transform = 'scaleX(' + f3(Math.max(.02, 2 * e - 1)) + ')';
    // s10: the powers slide under the crown, one by one, and turn red
    for (let i = 0; i < 4; i++) {
      const p = eio(P(t, T.pw.go + i * .3, T.pw.go + i * .3 + .45)), el = $('pw' + i);
      el.style.left = f1(lerp(T.pw.from[i][0], T.pw.to[i][0], p)) + 'px'; el.style.top = f1(lerp(T.pw.from[i][1], T.pw.to[i][1], p)) + 'px';
      el.style.background = mix(COL.blue, COL.red, p);
    }
    // s13: the governments tip over, each onto the next
    for (let i = 0; i < 5; i++) { const p = P(t, T.gov.fall + i * .42, T.gov.fall + i * .42 + .4); $('gvi' + i).style.transform = 'rotate(' + f1(T.gov.ang[i] * p * p) + 'deg)'; }
  };
}, T);

export const html = stage({ html: H, css, js, part: 1 });
await cli({ html, part: 1, dur });
