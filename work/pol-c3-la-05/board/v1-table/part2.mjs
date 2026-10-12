// POL-C3-LA-05 part 2: points 3, 4, 5, निष्कर्ष, the recap. 13 scenes on the kit.
//
//   node work/pol-c3-la-05/design/part2.mjs            -> out/layers/p2/{under,mask,overlay}.mov
//   node work/pol-c3-la-05/design/part2.mjs --cues     -> out/cues_p2.json
//   node work/pol-c3-la-05/design/part2.mjs --sheet    -> out/stills/p2/sheet_p2.png
//   node work/pol-c3-la-05/design/part2.mjs --stills 12.5,75 [--full]
//
// Every time is asked of the word clock by quoting what he says. Free zones as in part1.mjs;
// small (the recap) = everything above y 1680 except the round seat (750-1050, 1380-1680).
import { LOOK, load, stage, cli, browser, item, cue, table, strip, text, tag, band, pointCard, plaque, stamp, words, icon, box, disc, POINT_ICON } from './kit.mjs';

const { at, atw, scope, dur } = load(2);
let H = '', s;
const E = disc('explain'), Hd = disc('hidden');
const T = {};             // times the browser code below needs

table.seat(0);            // the countries sit at the table from part 1

// ---- s1 · to you · where we are; point 3
s = scope('s1');
H += tag({ html: 'Part 1 में', size: 64, at: s.at('Part'), out: s.at('अब इसके'), cx: true, y: 250, kind: 'brass' });
H += words({ items: [{ html: 'परिचय', at: s.at('परिचय') }, { html: 'पहले 2 points', at: s.at('पहले दो') }], out: s.at('अब इसके'), x: 0, w: 1080, y: 380, size: 60 });
table.turn(s.at('अब इसके'));
H += pointCard({ n: 3, text: 'व्यापार और आर्थिक वृद्धि', at: s.at('अब इसके'), atText: s.at('व्यापार'), y: 236 });

// ---- s2 · explaining · साफ्टा = दक्षिण एशिया मुक्त व्यापार क्षेत्र
s = scope('s2');
H += plaque({ text: 'साफ्टा', size: 124, at: s.at('साफ्टा'), cx: true, y: 300 });
H += stamp({ text: 'समझौता', size: 70, at: s.at('समझौता'), x: 640, y: 470, rot: -8, style: 'z-index:2' });
H += words({ items: [{ html: 'दक्षिण एशिया', at: s.at('दक्षिण') }, { html: 'मुक्त व्यापार', at: s.at('मुक्त') }, { html: 'क्षेत्र', at: s.at('क्षेत्र।') }],
  x: 0, w: 1080, y: 580, size: 62, gap: 16 });

// ---- s3 · explaining · V5 the trucks; आपसी व्यापार, आर्थिक साझेदारी
s = scope('s3');
H += band({ html: `आपसी व्यापार ${icon('up', 58, 'var(--teal)', 'vertical-align:-8px')}`, at: s.at('आपसी'), out: s.at('आर्थिक') });
H += band({ html: 'आर्थिक साझेदारी मज़बूत', at: s.at('आर्थिक') });

// ---- s4 · explaining · free trade = the tax barrier between two member countries drops, the goods cross
s = scope('s4');
T.crate = s.at('सामान'); T.stop = s.at('लेन-देन'); T.bar = s.at('कर,'); T.drop = s.at('कम'); T.go = T.drop + .25;
H += tag({ html: 'सदस्य देश', size: 48, kind: 'brass', at: s.at('सदस्य'), x: 175, y: 470 });
H += tag({ html: 'सदस्य देश', size: 48, kind: 'brass', at: s.at('सदस्य') + .1, x: 655, y: 470 });
H += box(`${icon('crate', 130, '#b9803f')}<b>सामान</b>`, { id: 'crate', at: T.crate, x: 220, y: 600, cls: 'crate', fx: 'drop', cue: 'knock' });
H += box('<div id="gate"><i></i></div>', { id: 'gatebox', at: T.bar, x: 500, y: 600, w: 80, h: 240, fx: 'drop', cue: 'knock' });
H += tag({ html: 'कर', size: 60, kind: 'coral', at: s.at('कर,'), x: 372, y: 866 });
H += tag({ html: '= टैक्स', size: 48, at: s.at('टैक्स'), x: 520, y: 872 });
cue('slide', T.drop, .3); cue('slide', T.go, .5);
H += band({ html: 'मुक्त व्यापार =', at: s.at('मुक्त'), out: T.drop });
H += band({ html: 'मुक्त व्यापार = <b style="color:var(--maroon)">कर कम</b>', at: T.drop });

// ---- s5 · to you · point 4
s = scope('s5');
H += tag({ html: 'समाज का विकास भी ज़रूरी', size: 60, at: s.at('समाज'), out: s.at('चौथा'), cx: true, y: 420 });
table.turn(s.at('चौथा'));
H += pointCard({ n: 4, text: 'सामाजिक और सांस्कृतिक विकास', at: s.at('चौथा'), atText: s.at('सामाजिक'), y: 236 });

// ---- s6 · explaining · शिक्षा स्वास्थ्य विज्ञान तकनीकी; V6; एक-दूसरे की मदद
s = scope('s6');
{
  const tv = s.shots[0].t0, items = [['book', 'शिक्षा', 'शिक्षा'], ['steth', 'स्वास्थ्य', 'स्वास्थ्य'], ['flask', 'विज्ञान', 'विज्ञान'], ['gear', 'तकनीकी', 'तकनीकी']];
  items.forEach(([ic, w, ph], i) => {
    const t = s.at(ph);
    H += box(`${icon(ic, 96, i === 1 ? 'var(--coral)' : 'var(--maroon)')}<b>${w}</b>`, { at: t, out: tv, x: E.cx - 300 + (i % 2) * 320, y: E.cy - 250 + Math.floor(i / 2) * 260, w: 280, h: 230, cls: 'tile', fx: 'drop', cue: false });
    cue('pluck', t);
  });
  H += band({ html: 'अपने अनुभव साझा करके', at: s.at('अनुभव'), out: s.at('एक-दूसरे') });
  H += band({ html: 'एक-दूसरे के विकास में मदद', at: s.at('एक-दूसरे'), kind: 'brass' });
  // arrows running round the ring from seat to seat
  const ta = s.at('एक-दूसरे'), rr = E.r + 92, segs = [[-172, -128], [-118, -74], [-64, -20], [-8, 30], [150, 188]];
  let svg = '';
  segs.forEach(([a0, a1], i) => {
    const p = a => [E.cx + rr * Math.cos(a * Math.PI / 180), E.cy + rr * Math.sin(a * Math.PI / 180)];
    const [x0, y0] = p(a0), [x1, y1] = p(a1), len = Math.ceil(rr * (a1 - a0) * Math.PI / 180), id = `rg${i}`;
    const tan = (a1 + 90) * Math.PI / 180, hx = (k) => `${(x1 - 22 * Math.cos(tan) + k * 13 * Math.sin(tan)).toFixed(1)} ${(y1 - 22 * Math.sin(tan) - k * 13 * Math.cos(tan)).toFixed(1)}`;
    item(id, { at: ta + i * .12, fx: 'draw', len, d: .35 }); item(`${id}h`, { at: ta + i * .12 + .3, fx: 'fade', d: .08 });
    svg += `<path id="${id}" class="svi" d="M${x0.toFixed(1)} ${y0.toFixed(1)} A${rr} ${rr} 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}" stroke-dasharray="${len}" stroke-dashoffset="${len}"/><path id="${id}h" class="svi" d="M${hx(1)} L${x1.toFixed(1)} ${y1.toFixed(1)} L${hx(-1)}"/>`;
  });
  cue('slide', ta, .6);
  H += `<svg class="arw" width="1080" height="1920" fill="none" stroke="var(--cream)" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 2px 2px rgba(0,0,0,.6))">${svg}</svg>`;
}

// ---- s7 · to you · point 5
s = scope('s7');
table.turn(s.at('पाँचवाँ'));
H += pointCard({ n: 5, text: 'चुनौतियाँ और रुकावटें', at: s.at('पाँचवाँ'), atText: s.at('चुनौतियाँ'), y: 236 });

// ---- s8 · to you · ध्यान से: "कमियाँ क्यों लिखें?" — यही point answer को पूरा बनाता है
s = scope('s8');
H += tag({ html: 'ध्यान से सुनना!', kind: 'coral', size: 66, at: s.at('ध्यान'), cx: true, y: 200, rot: -3 });
H += box('<div class="bub">सवाल योगदान का है…<br><b>तो कमियाँ क्यों लिखें?</b></div>', { at: s.at('सवाल'), out: s.at('लेकिन'), cx: true, y: 360, fx: 'pop', cue: 'slide' });
H += stamp({ html: 'यही point<br>answer को पूरा बनाता है', size: 62, at: s.at('यही'), cx: true, y: 400, rot: -4, style: 'text-align:center;line-height:1.25' });

// ---- s9 · hidden · the table cracks: three named causes; what it should have achieved vs what it did
s = scope('s9');
{
  const tc = [s.at('राजनीतिक'), s.at('सरहद'), s.at('अविश्वास')];
  tc.forEach((t, i) => table.crack(i, t));
  H += words({ items: [{ html: `${icon('crack', 46, '#fff7ee', 'vertical-align:-6px;margin-right:10px')}आपसी राजनीतिक तनाव`, at: tc[0] }, { html: `${icon('crack', 46, '#fff7ee', 'vertical-align:-6px;margin-right:10px')}सरहद पर आतंकवाद`, at: tc[1] },
    { html: `${icon('crack', 46, '#fff7ee', 'vertical-align:-6px;margin-right:10px')}आपसी अविश्वास`, at: tc[2] }], kind: 'coral', x: 0, w: 1080, y: 110, size: 58, gap: 16, cueKind: 'knock' });
  const tw = s.at('जितनी'), tu = s.at('उतनी');
  H += box('<div class="barw"><i>जितनी सफलता मिलनी चाहिए थी</i></div>', { at: tw, x: 60, y: 1370, w: 960, h: 110, fx: 'grow', cue: 'slide', style: 'transform-origin:0 50%' });
  H += box('<div class="barf"><i>उतनी नहीं मिल पाई</i></div>', { at: tu, x: 60, y: 1510, w: 560, h: 110, fx: 'grow', cue: 'slide', style: 'transform-origin:0 50%' });
}

// ---- s10 · explaining · निष्कर्ष: अपार संभावनाएँ · आपसी मतभेद → रफ्तार धीमी · फिर भी अहम मंच
s = scope('s10');
{
  const tk = s.at('लेकिन');
  H += plaque({ text: 'निष्कर्ष', size: 100, at: s.at('निष्कर्ष'), cx: true, y: 290 });
  H += tag({ html: 'अपार संभावनाएँ', kind: 'teal', size: 52, at: s.at('अपार'), out: tk, x: 175, y: 640 });
  let fan = '';
  [-28, -14, 0, 14, 28].forEach((a, i) => { fan += `<i style="transform:rotate(${a}deg)">${icon('up', 74, 'var(--teal)')}</i>`; });
  H += box(fan, { at: s.at('अपार'), out: tk, x: 200, y: 470, w: 280, h: 160, cls: 'fan', fx: 'pop', cue: 'pluck' });
  H += box('<div id="dial"><svg width="260" height="160" viewBox="0 0 260 160"><path d="M20 140 A110 110 0 0 1 240 140" fill="none" stroke="#2b1d14" stroke-width="22"/><path d="M20 140 A110 110 0 0 1 88 38" fill="none" stroke="#e2553f" stroke-width="16"/><path d="M88 38 A110 110 0 0 1 240 140" fill="none" stroke="#2f7d6d" stroke-width="16"/><g id="ndl"><path d="M130 140 L130 44" stroke="#f6eedc" stroke-width="9" stroke-linecap="round"/></g><circle cx="130" cy="140" r="14" fill="#d9a841"/></svg></div>',
    { at: s.at('रफ्तार'), out: tk, x: 580, y: 470, w: 260, h: 170, fx: 'pop', cue: 'knock' });
  T.dial = [s.at('रफ्तार'), s.at('धीमा')];
  H += tag({ html: 'रफ्तार धीमी', kind: 'coral', size: 50, at: s.at('धीमा'), out: tk, x: 590, y: 650 });
  H += tag({ html: 'आपसी मतभेद', kind: 'dark', size: 56, at: s.at('मतभेद'), out: tk, cx: true, y: 800 });
  table.heal(tk);
  H += tag({ html: 'फिर भी', size: 56, at: tk, cx: true, y: 470 });
  H += tag({ html: 'क्षेत्रीय विकास के लिए', size: 56, at: s.at('क्षेत्रीय'), cx: true, y: 580 });
  H += tag({ html: 'आज भी एक अहम मंच', kind: 'brass', size: 66, at: s.at('अहम'), cx: true, y: 700 });
  table.glow(s.at('मंच'), s.t1);
}

// ---- s11 · small · the recap: each point's picture again in the disc, its card in the list
s = scope('s11');
{
  const ts = ['पहला', 'दूसरा', 'तीसरा', 'चौथा', 'पाँचवाँ'].map(w => atw(w, s.t0));
  const titles = ['क्षेत्रीय सहयोग की शुरुआत', 'गरीबी और बेरोज़गारी से मुकाबला', 'साफ्टा: व्यापार और आर्थिक वृद्धि', 'सामाजिक और सांस्कृतिक विकास', 'चुनौतियाँ और रुकावटें'];
  H += tag({ html: '5 points, एक बार फिर', kind: 'brass', size: 52, at: s.at('चलो'), out: ts[0], cx: true, y: 1100 });
  titles.forEach((tt, i) => {
    H += box(`<b class="rn ${i === 4 ? 'rc' : ''}">${i + 1}</b><span>${tt}</span>`, { at: ts[i], out: s.t1, x: 36, y: 1086 + i * 114, cls: 'rrow', fx: 'slideL', cue: 'knock' });
    cue('chime', ts[i] + .05);
  });
  table.crack(0, ts[4] + .3); table.crack(2, ts[4] + .55); table.heal(s.t1 - .4);
}

// ---- s12 · to you · परिचय + 5 points + निष्कर्ष = 4 नंबर पक्के; Notes
s = scope('s12');
{
  const tt = [s.at('परिचय'), s.at('points'), s.at('निष्कर्ष')];
  const rows = ['परिचय', '5 points', 'निष्कर्ष'];
  rows.forEach((r, i) => { H += box(`<span>${r}</span><i id="sk${i}" class="sub">${icon('tick', 56, 'var(--teal)')}</i>`, { at: [s.at('शुरुआत'), s.at('ये पाँच'), s.at('आखिर')][i], x: 210, y: 200 + i * 118, w: 660, cls: 'skr', fx: 'slideL', cue: 'slide' }); item(`sk${i}`, { at: tt[i] + .25, fx: 'pop' }); cue('tick', tt[i] + .25); });
  H += stamp({ text: '4 नंबर पक्के', size: 84, at: s.at('4'), cx: true, y: 580, rot: -6, color: 'teal' });
  H += tag({ html: 'पूरा answer → Notes में', kind: 'dark', size: 56, at: s.at('Notes'), cx: true, y: 720 });
}
// ---- s13 · to you · 90% की ओर
s = scope('s13');
H += tag({ html: '90% की ओर', kind: 'brass', size: 76, at: s.at('90%'), cx: true, y: 420 });

// ---- the strip: from the start, two cards already laid
{
  const r = scope('s11').t0, rs = ['पहला', 'दूसरा', 'तीसरा', 'चौथा', 'पाँचवाँ'].map(w => atw(w, r));
  H += strip({ at: 0, intro: 0, filled: 2, fill: [null, null, scope('s2').t0, scope('s6').t0, scope('s8').t0], end: at('s10', 'निष्कर्ष'),
    ticks: [at('s12', 'परिचय') + .25, at('s12', 'points') + .25, at('s12', 'निष्कर्ष') + .25],
    now: [[at('s1', 'परिचय'), 'p'], [at('s1', 'पहले दो'), 1], [at('s1', 'अब इसके'), 2], [at('s5', 'चौथा'), 3], [at('s7', 'पाँचवाँ'), 4], [at('s10', 'निष्कर्ष'), 'n'],
      [r, 'off'], ...rs.map((t, i) => [t, i]), [scope('s12').t0, 'off']] });
}

const css = `

.crate{display:flex;flex-direction:column;align-items:center}
.crate b{font:800 44px/1 Baloo,Hind;color:var(--cream);margin-top:6px;-webkit-text-stroke:6px rgba(43,29,20,.85);paint-order:stroke fill}
#gate{position:relative;width:80px;height:240px}
#gate i{position:absolute;left:0;right:0;bottom:0;height:100%;border-radius:8px;border:5px solid #2b1d14;box-sizing:border-box;
 background:repeating-linear-gradient(-45deg,#e2553f 0 22px,#f6eedc 22px 44px);box-shadow:0 8px 12px rgba(0,0,0,.45)}
.tile{background:var(--cream);border-radius:16px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;box-shadow:0 6px 0 rgba(40,20,8,.25),0 10px 18px rgba(20,8,2,.35)}
.tile b{font:800 52px/1.1 Baloo,Hind;color:var(--ink)}
.bub{background:var(--cream);border-radius:40px;padding:26px 44px 18px;font:700 50px/1.35 Hind;color:var(--ink);text-align:center;box-shadow:0 10px 22px rgba(20,8,2,.45);position:relative;white-space:nowrap}
.bub b{font:800 60px/1.3 Baloo;color:var(--coral)}
.bub:after{content:'';position:absolute;left:50%;bottom:-34px;margin-left:-20px;border:20px solid transparent;border-top:24px solid var(--cream)}
.barw,.barf{height:110px;border-radius:14px;display:flex;align-items:center;padding:0 30px;box-sizing:border-box;font:800 52px/1 Baloo,Hind;white-space:nowrap}
.barw{border:6px dashed var(--cream);color:var(--cream);background:rgba(30,15,6,.35)}
.barf{background:var(--coral);color:#fff7ee;box-shadow:0 8px 14px rgba(0,0,0,.4)}
.barw i,.barf i{font-style:normal;padding-top:8px}
.fan{display:flex;justify-content:center;align-items:flex-end}
.fan i{display:block;margin:0 -12px;transform-origin:50% 100%}
.rrow{display:flex;align-items:center;gap:16px;height:100px;background:var(--cream);border-radius:14px;padding:0 26px 0 12px;box-shadow:0 5px 0 rgba(40,20,8,.25),0 8px 14px rgba(20,8,2,.35);white-space:nowrap}
.rrow span{font:800 46px/1 Baloo,Hind;color:var(--ink);padding-top:8px}
.rn{font:400 52px/76px Yatra;width:76px;height:76px;border-radius:50%;text-align:center;color:#3a2410;background:radial-gradient(circle at 40% 35%,#f3d27a,#c8962c 70%,#9c701c)}
.rn.rc{background:radial-gradient(circle at 40% 35%,#f59a80,#e2553f 70%,#b63a27);color:#fff7ee}
.skr{display:flex;align-items:center;justify-content:space-between;height:100px;padding:0 30px;background:var(--cream);border-radius:14px;border-left:14px solid var(--brass);box-shadow:0 6px 0 rgba(40,20,8,.25),0 10px 18px rgba(20,8,2,.35);font:800 62px/1 Baloo,Hind}
.skr span{padding-top:10px}
`;
const js = browser(function (T) {
  window.frame = t => {
    // the barrier drops low; the goods roll across
    const g = document.querySelector('#gate i'); if (g) g.style.height = f1(100 - 76 * eout(P(t, T.drop, T.drop + .3))) + '%';
    const c = $('crate'); if (c && t >= T.crate) c.style.left = f1(220 + 150 * eio(P(t, T.crate + .3, T.stop)) + 330 * eio(P(t, T.go, T.go + .55))) + 'px';
    // the speed needle falls back
    const n = $('ndl'); if (n) n.setAttribute('transform', 'rotate(' + f1(lerp(58, -62, eio(P(t, T.dial[0] + .2, T.dial[1] + .4)))) + ' 130 140)');
  };
}, T);
await cli({ html: stage({ html: H, css, js, part: 2 }), part: 2, dur });
