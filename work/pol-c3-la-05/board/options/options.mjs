// POL-C3-LA-05 redesign: four directions, three frames each, as stills (no video is rendered).
//   node work/pol-c3-la-05/board/options/options.mjs   -> board/options/out/<opt>_<frame>.png
// Drawing only: real clip stills, the real presenter cut-out, Natural Earth land through d3.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderStills } from '../../../../tools/reel/layers.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const VID = path.resolve(HERE, '../..'), ROOT = path.resolve(VID, '../..');
const b64 = (f, mime) => `data:${mime};base64,${fs.readFileSync(f).toString('base64')}`;
const SRC = n => b64(path.join(HERE, 'src', n + '.jpg'), 'image/jpeg');
const PRES = b64(path.join(VID, 'assets/presenter_cutout.png'), 'image/png');
const F = {
  poppinsX: 'docs/history-poc/fonts/ttf/Poppins-ExtraBold.ttf', poppinsB: 'docs/history-poc/fonts/ttf/Poppins-Black.ttf',
  mukta: 'docs/history-poc/fonts/ttf/Mukta-ExtraBold.ttf', baloo: 'docs/history-poc/fonts/ttf/Baloo2[wght].ttf', hind: 'docs/history-poc/fonts/ttf/Hind-Bold.ttf',
  rozha: 'docs/history-poc/fonts/ttf/RozhaOne-Regular.ttf', tiro: 'assets/fonts/TiroDevanagariHindi-Regular.ttf', khand: 'assets/fonts/Khand-Bold.ttf',
  anek: 'assets/fonts/AnekDevanagari[wdth,wght].ttf',
};
const face = (fam, file, w = '400') => `@font-face{font-family:${fam};font-weight:${w};src:url(${b64(path.join(ROOT, file), 'font/ttf')}) format('truetype')}`;
const FONTS = [face('PopX', F.poppinsX, '800'), face('PopB', F.poppinsB, '900'), face('Mukta', F.mukta, '800'), face('Baloo', F.baloo, '400 800'),
  face('Hind', F.hind, '700'), face('Rozha', F.rozha), face('Tiro', F.tiro), face('Khand', F.khand, '700'), face('Anek', F.anek, '100 900')].join('');
const D3 = ['d3-array.min.js', 'd3-geo.min.js'].map(f => fs.readFileSync(path.join(ROOT, 'tools/reel/vendor', f), 'utf8')).join('\n;');
const LAND = fs.readFileSync(path.join(VID, 'assets/data/land10m_52-106E_-6-46N.geojson'), 'utf8');
const LL = JSON.parse(fs.readFileSync(path.join(VID, 'assets/map.json'), 'utf8')).anchors_lonlat;
const NAMES = { afghanistan: 'अफ़ग़ानिस्तान', pakistan: 'पाकिस्तान', india: 'भारत', nepal: 'नेपाल', bhutan: 'भूटान', bangladesh: 'बांग्लादेश', srilanka: 'श्रीलंका', maldives: 'मालदीव' };

// the presenter cut-out: crop pixel (cx, cy) lands at (x0 + s*cx, y0 + s*cy)
const pres = (s, x0, y0, extra = '') => `<img src="${PRES}" style="position:absolute;left:${x0}px;top:${y0}px;width:${1120 * s}px;height:${960 * s}px;${extra}">`;
// a caption line: words, with the spoken one marked
const capWords = (words, active) => words.map((w, i) => i === active ? `<b class="act">${w}</b>` : `<span class="${i > active ? 'up' : ''}">${w}</span>`).join(' ');
const CAP = {
  f1: [['गरीबी,', 'भुखमरी', 'और', 'बेरोजगारी', 'को', 'मिलकर', 'खत्म'], 5],
  f2: [['और', 'यही', 'है', 'अगला', 'point,', 'गरीबी', 'और'], 3],
  f3: [['मालदीव,', 'पाकिस्तान', 'और', 'श्रीलंका,', 'यानी', 'कुल', 'आठ'], 3],
};
const cap = (k, cls = '') => `<div class="cap ${cls}">${capWords(...CAP[k])}</div>`;

/** a map drawn by d3 in the page: rect to fit the region into, colours, and pins */
function mapScript({ rect, sea, land, coast, coastW = 2, grat = null, pins = null, glow = null, extraLand = '' }) {
  return `<svg id="mp" width="1080" height="1920" style="position:absolute;left:0;top:0"></svg><script>
${D3}
(function(){const LAND=${LAND};const LL=${JSON.stringify(LL)};
const box={type:'MultiPoint',coordinates:[[60,-1],[98,-1],[98,39.4],[60,39.4],[79,39.4],[79,-1]]};
const pr=d3.geoMercator().fitExtent(${JSON.stringify(rect)},box);const p=d3.geoPath(pr);
let s='<rect width="1080" height="1920" fill="${sea}"/>';
${grat ? `s+='<path d="'+p(d3.geoGraticule().step([5,5])())+'" fill="none" stroke="${grat}" stroke-width="1.2"/>';` : ''}
s+='<path d="'+p(LAND)+'" fill="${land}" stroke="${coast}" stroke-width="${coastW}" stroke-linejoin="round" ${extraLand}/>';
document.getElementById('mp').innerHTML=s;
window.PT=k=>pr(LL[k]);
document.addEventListener('DOMContentLoaded',()=>{${pins || ''}});
})();</script>`;
}

const page = (body, css) => `<!doctype html><html><head><meta charset="utf-8"><style>${FONTS}
html,body{margin:0;background:#000}#st{position:relative;width:1080px;height:1920px;overflow:hidden}
.ab{position:absolute}${css}</style></head><body><div id="st">${body}</div>
<script>window.render=()=>{};window.READY=document.fonts.ready;</script></body></html>`;

// =====================================================================  A · शिखर रात (summit night)
const A = {
  css: `#st{background:radial-gradient(ellipse 700px 620px at 540px 1500px,#2b3550 0,#141b2b 55%,#0b101b 100%);font-family:Mukta}
.rings{position:absolute;left:-460px;top:560px;width:2000px;height:2000px;border-radius:50%;background:repeating-radial-gradient(circle,transparent 0 118px,rgba(232,177,74,.07) 118px 120px)}
.prog{position:absolute;left:60px;right:60px;top:60px;display:flex;gap:14px}
.prog i{flex:1;height:10px;border-radius:5px;background:rgba(244,241,234,.18)}.prog i.d{background:#e8b14a}.prog i.c{background:#e8b14a;box-shadow:0 0 14px 3px rgba(232,177,74,.6)}
.eb{font:800 40px/1 Mukta;color:#e8b14a}
.film{position:absolute;left:0;top:120px;width:1080px;height:900px;background-size:cover;background-position:50% 45%;-webkit-mask-image:linear-gradient(#000 70%,transparent)}
.big{font:800 84px/1.15 PopX;color:#f4f1ea;text-shadow:0 4px 20px rgba(0,0,0,.6)}
.strk{position:relative;display:inline-block}.strk:after{content:'';position:absolute;left:-6px;right:-6px;top:52%;height:9px;background:#e8b14a;border-radius:4px;transform:rotate(-2deg)}
.pill{display:inline-block;background:#e8b14a;color:#141b2b;font:800 64px/1 PopX;padding:22px 36px 12px;border-radius:14px}
.cap{position:absolute;left:40px;right:40px;top:1730px;text-align:center;font:800 54px/1.2 Mukta;color:#f4f1ea;text-shadow:0 3px 10px rgba(0,0,0,.8)}
.cap .act{color:#e8b14a}.cap .up{opacity:.55}
.num{font:900 330px/1 PopB;color:transparent;-webkit-text-stroke:5px #e8b14a}
.ttl{font:800 92px/1.15 PopX;color:#f4f1ea}
.rule{width:140px;height:8px;background:#e8b14a;border-radius:4px}
.lab{font:800 42px/1 PopX;color:#f4f1ea;background:rgba(11,16,27,.72);padding:12px 18px 6px;border-radius:10px;white-space:nowrap}`,
  prog: c => `<div class="prog">${[0, 1, 2, 3, 4].map(i => `<i class="${i < c ? 'd' : i === c ? 'c' : ''}"></i>`).join('')}</div>`,
  f1() {
    return page(`<div class="rings"></div><div class="film" style="background-image:url(${SRC('V3')})"></div>${this.prog(1)}
<div class="ab eb" style="left:70px;top:110px">Point 2 · मुख्य उद्देश्य</div>
<div class="ab big" style="left:60px;top:740px;font-size:68px;white-space:nowrap"><span class="strk">गरीबी</span> · <span class="strk">भुखमरी</span> · <span class="strk">बेरोज़गारी</span></div>
<div class="ab" style="left:60px;top:850px"><span class="pill">मिलकर खत्म</span></div>
${pres(.8, 110, 1152)}${cap('f1')}`, this.css);
  },
  f2() {
    return page(`<div class="rings"></div><div class="film" style="background-image:url(${SRC('V3')});opacity:.28;filter:blur(6px) saturate(.6)"></div>${this.prog(1)}
<div class="ab" style="left:70px;top:150px"><div class="eb">Point</div><div class="num">02</div></div>
<div class="ab" style="left:70px;top:560px"><div class="rule"></div><div class="ttl" style="margin-top:22px">गरीबी और बेरोज़गारी<br>से मुकाबला</div></div>
${pres(1.2, -104, 900)}${cap('f2')}`, this.css);
  },
  f3() {
    const pins = `let h='';for(const k in ${JSON.stringify(NAMES)}){const [x,y]=PT(k);const n=${JSON.stringify(NAMES)}[k];const side={afghanistan:[-80,-70],pakistan:[-60,40],india:[24,-24],nepal:[-70,-74],bhutan:[-30,-74],bangladesh:[22,10],srilanka:[26,-20],maldives:[26,-20]}[k];
h+='<div class="ab" style="left:'+(x-11)+'px;top:'+(y-11)+'px;width:22px;height:22px;border-radius:50%;background:#e8b14a;box-shadow:0 0 0 8px rgba(232,177,74,.25),0 0 22px 6px rgba(232,177,74,.6)"></div>';
h+='<div class="ab lab" style="left:'+(x+side[0])+'px;top:'+(y+side[1])+'px">'+n+'</div>';}document.getElementById('pins').innerHTML=h;`;
    return page(mapScript({ rect: [[0, 330], [1080, 1640]], sea: '#0b101b', land: '#1d2840', coast: '#e8b14a', coastW: 2.4, grat: 'rgba(232,177,74,.08)', pins }) +
      `<div id="pins"></div><div class="ab" style="left:70px;top:90px"><div class="eb">SAARC</div><div class="ttl" style="font-size:80px;margin-top:10px">सार्क के सदस्य देश</div></div>
<div class="ab num" style="right:60px;top:60px;font-size:240px">8</div>${cap('f3')}`, this.css);
  },
};

// =====================================================================  B · रंगों वाला explainer
const PC = ['#16808f', '#e5761b', '#3b57d4', '#2d9a58', '#d8433b'];
const B = {
  css: `#st{background:#eef2f7;background-image:radial-gradient(#d3dbe6 2.2px,transparent 2.6px);background-size:36px 36px;font-family:Hind;color:#1c2433}
.prog{position:absolute;left:0;right:0;top:54px;display:flex;justify-content:center;gap:18px}
.prog i{width:64px;height:64px;border-radius:50%;background:#fff;border:5px solid #cfd8e3;box-sizing:border-box;font:800 34px/56px Baloo;text-align:center;font-style:normal;color:#9aa8b8}
.prog i.d,.prog i.c{border:none;color:#fff;line-height:66px}.prog i.c{width:84px;height:84px;margin-top:-10px;line-height:88px;font-size:46px;box-shadow:0 8px 18px rgba(0,0,0,.18)}
.card{position:absolute;border:14px solid #fff;border-radius:44px;background-size:cover;background-position:50% 40%;box-shadow:0 24px 50px rgba(28,36,51,.25)}
.chip{display:inline-flex;align-items:center;gap:14px;background:#fff;border-radius:999px;padding:16px 34px 8px;font:800 58px/1 Baloo;box-shadow:0 8px 18px rgba(28,36,51,.14)}
.badge{position:absolute;width:150px;height:150px;border-radius:40px;color:#fff;font:800 108px/164px Baloo;text-align:center;box-shadow:0 12px 24px rgba(0,0,0,.2);transform:rotate(-6deg)}
.blob{position:absolute;border-radius:50%}
.cap{position:absolute;left:0;right:0;top:1726px;text-align:center}.cap>*{font:700 52px/1 Hind}
.cap{display:flex;justify-content:center;gap:12px}.cap span,.cap b{background:#fff;padding:18px 12px 8px;color:#1c2433}.cap span:first-child{border-radius:16px 0 0 16px;padding-left:30px}.cap :last-child{border-radius:0 16px 16px 0;padding-right:30px}
.cap{gap:0}.cap .act{color:${PC[1]}}.cap .up{color:#9aa8b8}
.title{font:800 96px/1.12 Baloo}
.lab{font:800 40px/1 Baloo;background:#fff;padding:12px 18px 4px;border-radius:12px;white-space:nowrap;box-shadow:0 6px 14px rgba(28,36,51,.15)}`,
  prog: c => `<div class="prog">${[0, 1, 2, 3, 4].map(i => `<i class="${i < c ? 'd' : i === c ? 'c' : ''}" style="${i <= c ? `background:${PC[i]}` : ''}">${i < c ? '✓' : i + 1}</i>`).join('')}</div>`,
  f1() {
    return page(`${this.prog(1)}<div class="card" style="left:70px;top:190px;width:940px;height:700px;background-image:url(${SRC('V3')});transform:rotate(-1.2deg)"></div>
<div class="badge" style="left:40px;top:150px;background:${PC[1]}">2</div>
<div class="ab" style="left:0;right:0;top:930px;display:flex;justify-content:center;gap:16px">${['गरीबी', 'भुखमरी', 'बेरोज़गारी'].map(w => `<span class="chip" style="text-decoration:line-through;text-decoration-color:${PC[1]};text-decoration-thickness:8px">${w}</span>`).join('')}</div>
<div class="ab" style="left:0;right:0;top:1060px;text-align:center"><span class="chip" style="background:${PC[1]};color:#fff">मिलकर खत्म ✊</span></div>
<div class="blob" style="left:250px;top:1290px;width:580px;height:580px;background:${PC[1]}"></div>${pres(.8, 110, 1152)}${cap('f1')}`, this.css);
  },
  f2() {
    return page(`${this.prog(1)}<div class="ab" style="left:70px;top:220px;width:940px;background:#fff;border-radius:44px;padding:70px 60px 54px;box-sizing:border-box;box-shadow:0 24px 50px rgba(28,36,51,.18)">
<div style="display:flex;align-items:center;gap:30px"><div style="width:150px;height:150px;border-radius:40px;background:${PC[1]};color:#fff;font:800 108px/164px Baloo;text-align:center">2</div>
<svg width="130" height="130" viewBox="0 0 100 100"><path d="M12 50 H88 Q86 82 50 86 Q14 82 12 50 Z" fill="${PC[1]}"/><path d="M24 48 Q30 26 50 24 Q70 26 76 48 Z" fill="${PC[1]}" opacity=".45"/></svg></div>
<div class="title" style="margin-top:34px">गरीबी और बेरोज़गारी<br><span style="color:${PC[1]}">से मुकाबला</span></div></div>
<div class="blob" style="left:130px;top:1000px;width:820px;height:820px;background:${PC[1]};opacity:.95"></div>${pres(1.2, -104, 900)}${cap('f2')}`, this.css);
  },
  f3() {
    const COLS = ['#16808f', '#e5761b', '#3b57d4', '#2d9a58', '#d8433b', '#8b4fd0', '#c2185b', '#0b8a6a'];
    const pins = `let h='',i=0;for(const k in ${JSON.stringify(NAMES)}){const [x,y]=PT(k);const n=${JSON.stringify(NAMES)}[k];const c=${JSON.stringify(COLS)}[i++];const side={afghanistan:[-110,-82],pakistan:[-80,34],india:[30,-30],nepal:[-80,-84],bhutan:[-30,-84],bangladesh:[30,8],srilanka:[34,-22],maldives:[34,-22]}[k];
h+='<div class="ab" style="left:'+(x-24)+'px;top:'+(y-24)+'px;width:48px;height:48px;border-radius:50%;background:'+c+';color:#fff;font:800 30px/54px Baloo;text-align:center;box-shadow:0 6px 12px rgba(0,0,0,.25)">'+i+'</div>';
h+='<div class="ab lab" style="left:'+(x+side[0])+'px;top:'+(y+side[1])+'px;color:'+c+'">'+n+'</div>';}document.getElementById('pins').innerHTML=h;`;
    return page(mapScript({ rect: [[30, 330], [1050, 1620]], sea: '#cfe3f3', land: '#fbfaf6', coast: '#8fa6c0', coastW: 2.4, grat: 'rgba(255,255,255,.55)', pins }) +
      `<div id="pins"></div><div class="ab" style="left:70px;top:90px"><div class="title" style="font-size:76px">सार्क के सदस्य देश</div></div>
<div class="ab" style="right:60px;top:80px;background:${PC[1]};color:#fff;border-radius:30px;font:800 72px/1 Baloo;padding:30px 34px 18px">8 देश</div>${cap('f3')}`, this.css);
  },
};

// =====================================================================  C · पूरा पर्दा (full-bleed reel)
const C = {
  css: `#st{font-family:Mukta;background:#111}
.bleed{position:absolute;inset:0;background-size:cover;background-position:50% 50%}
.shade{position:absolute;inset:0;background:linear-gradient(rgba(0,0,0,.62),rgba(0,0,0,0) 32%,rgba(0,0,0,0) 52%,rgba(0,0,0,.78) 78%)}
.prog{position:absolute;left:40px;right:40px;top:40px;display:flex;gap:10px}.prog i{flex:1;height:7px;border-radius:4px;background:rgba(255,255,255,.35)}.prog i.d{background:#fff}.prog i.c{background:linear-gradient(90deg,#ffd23f 55%,rgba(255,255,255,.35) 55%)}
.k{font:800 104px/1.08 Mukta;color:#fff;text-shadow:0 6px 24px rgba(0,0,0,.55)}
.hl{background:#ffd23f;color:#111;padding:6px 22px 0;border-radius:10px;text-shadow:none;display:inline-block}
.x{position:relative;display:inline-block}.x:after{content:'';position:absolute;left:-8px;right:-8px;top:50%;height:12px;background:#ff4b3e;transform:rotate(-3deg);border-radius:6px}
.cap{position:absolute;left:30px;right:30px;top:1716px;text-align:center;font:800 54px/1.15 Mukta;color:#fff;-webkit-text-stroke:10px #000;paint-order:stroke fill}
.cap .act{color:#ffd23f}.cap .up{opacity:.6}
.lab{font:800 46px/1 Mukta;color:#111;background:#ffd23f;padding:12px 20px 4px;border-radius:10px;white-space:nowrap}`,
  prog: c => `<div class="prog">${[0, 1, 2, 3, 4].map(i => `<i class="${i < c ? 'd' : i === c ? 'c' : ''}"></i>`).join('')}</div>`,
  f1() {
    return page(`<div class="bleed" style="background-image:url(${SRC('V3')})"></div><div class="shade"></div>${this.prog(1)}
<div class="ab" style="left:60px;top:110px;font:800 44px/1 Mukta;color:#ffd23f">POINT 2 · मुख्य उद्देश्य</div>
<div class="ab k" style="left:60px;top:190px"><span class="x">गरीबी</span><br><span class="x">भुखमरी</span><br><span class="x">बेरोज़गारी</span><br><span class="hl">मिलकर खत्म</span></div>
${pres(.82, 300, 1140, 'filter:drop-shadow(0 0 18px rgba(0,0,0,.6))')}${cap('f1')}`, this.css);
  },
  f2() {
    return page(`<div class="bleed" style="background-image:url(${SRC('V3')});filter:blur(14px) brightness(.45) saturate(.8);transform:scale(1.1)"></div>${this.prog(1)}
<div class="ab" style="left:60px;top:150px;font:400 380px/1 Rozha;color:#ffd23f">2</div>
<div class="ab k" style="left:60px;top:560px;font-size:110px">गरीबी और<br>बेरोज़गारी से<br><span class="hl">मुकाबला</span></div>
${pres(1.2, -104, 900, 'filter:drop-shadow(0 0 22px rgba(0,0,0,.6))')}${cap('f2')}`, this.css);
  },
  f3() {
    const pins = `let h='';for(const k in ${JSON.stringify(NAMES)}){const [x,y]=PT(k);const n=${JSON.stringify(NAMES)}[k];const side={afghanistan:[-110,-80],pakistan:[-80,36],india:[30,-30],nepal:[-90,-84],bhutan:[-30,-84],bangladesh:[30,10],srilanka:[34,-24],maldives:[34,-24]}[k];
h+='<div class="ab" style="left:'+(x-14)+'px;top:'+(y-14)+'px;width:28px;height:28px;border-radius:50%;background:#ffd23f;border:5px solid #111"></div>';
h+='<div class="ab lab" style="left:'+(x+side[0])+'px;top:'+(y+side[1])+'px">'+n+'</div>';}document.getElementById('pins').innerHTML=h;`;
    return page(`<div class="bleed" style="background-image:url(${SRC('V1')});filter:blur(10px) brightness(.35)"></div>` +
      mapScript({ rect: [[20, 300], [1060, 1640]], sea: 'rgba(0,0,0,0)', land: 'rgba(255,255,255,.12)', coast: '#fff', coastW: 3, pins }) +
      `<div id="pins"></div><div class="ab k" style="left:60px;top:90px;font-size:88px">सार्क के <span class="hl">8 देश</span></div>${cap('f3')}`, this.css);
  },
};

// =====================================================================  D · नक्शे की मेज़ (the atlas is the stage)
const D = {
  css: `#st{background:#143e3a;font-family:Tiro}
.dim{position:absolute;inset:0;background:rgba(10,30,28,.45)}
.stamps{position:absolute;left:0;right:0;top:46px;display:flex;justify-content:center;gap:16px}
.stamp{width:150px;height:118px;background:#f2e8d2;padding:9px;box-sizing:border-box;outline:5px dotted #f2e8d2;outline-offset:-2px;box-shadow:0 6px 10px rgba(0,0,0,.45)}
.stamp div{width:100%;height:100%;background-size:cover;background-position:center;display:flex;align-items:flex-end;justify-content:flex-end}
.stamp b{font:400 40px/1 Rozha;color:#f2e8d2;background:#8c2f24;padding:4px 10px 0}
.stamp.e div{background:#e4d6b8;border:3px dashed #b5a27c;box-sizing:border-box;justify-content:center;align-items:center}.stamp.e b{background:none;color:#b5a27c}
.post{position:absolute;background:#f6f0e2;padding:18px 18px 18px;box-shadow:0 22px 40px rgba(0,0,0,.45)}
.post div{width:100%;height:100%;background-size:cover;background-position:50% 40%}
.post i{position:absolute;left:0;right:0;bottom:12px;text-align:center;font:400 44px/1.1 Tiro;color:#3a2a1a;font-style:normal}
.tape{position:absolute;width:150px;height:44px;background:rgba(242,232,210,.75);transform:rotate(-8deg)}
.rib{display:inline-block;background:#f2e8d2;color:#2c241a;font:400 60px/1 Tiro;padding:24px 40px 10px;box-shadow:0 8px 16px rgba(0,0,0,.35);clip-path:polygon(0 0,100% 0,97% 50%,100% 100%,0 100%,3% 50%)}
.x{text-decoration:line-through;text-decoration-color:#8c2f24;text-decoration-thickness:7px}
.seal{width:200px;height:200px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#b5463a,#8c2f24 70%);color:#f2e8d2;font:400 140px/226px Rozha;text-align:center;box-shadow:0 10px 20px rgba(0,0,0,.45),inset 0 0 0 10px rgba(0,0,0,.12)}
.cap{position:absolute;left:40px;right:40px;top:1722px;text-align:center}.cap{font:400 56px/1.2 Tiro;color:#f2e8d2;text-shadow:0 3px 8px rgba(0,0,0,.8)}
.cap .act{color:#f0b65a;font-weight:400}.cap .up{opacity:.55}
.lab{font:400 44px/1 Tiro;color:#2c241a;white-space:nowrap;text-shadow:0 0 6px #e9dcc0,0 0 12px #e9dcc0}`,
  map: (pins, dim = true) => mapScript({ rect: [[-140, 120], [1220, 1700]], sea: '#143e3a', land: '#e9dcc0', coast: '#2c241a', coastW: 1.6, grat: 'rgba(233,220,192,.13)', pins }) + (dim ? '<div class="dim"></div>' : ''),
  stamps(c) {
    const pics = ['V2', 'V3', 'V5', 'V6', null];
    return `<div class="stamps">${pics.map((p, i) => i <= c && p ? `<div class="stamp"><div style="background-image:url(${SRC(p)})"><b>${i + 1}</b></div></div>` : `<div class="stamp e"><div><b>${i + 1}</b></div></div>`).join('')}</div>`;
  },
  f1() {
    return page(this.map('') + this.stamps(1) + `<div class="post" style="left:110px;top:250px;width:640px;height:700px;transform:rotate(-3deg)"><div style="background-image:url(${SRC('V3')})"></div></div>
<div class="tape" style="left:360px;top:232px"></div>
<div class="ab" style="left:560px;top:820px;transform:rotate(2deg)"><div class="rib" style="font-size:52px">मुख्य उद्देश्य</div></div>
<div class="ab" style="left:80px;top:1010px;display:flex;flex-direction:column;gap:14px;align-items:flex-start">
<div class="rib"><span class="x">गरीबी</span> · <span class="x">भुखमरी</span> · <span class="x">बेरोज़गारी</span></div>
<div class="rib" style="background:#8c2f24;color:#f2e8d2">मिलकर खत्म</div></div>
${pres(.8, 330, 1152)}${cap('f1')}`, this.css);
  },
  f2() {
    return page(this.map('') + this.stamps(1) + `<div class="ab" style="left:440px;top:240px"><div class="seal">2</div></div>
<div class="ab" style="left:0;right:0;top:480px;text-align:center"><div class="rib" style="font-size:82px;padding:34px 60px 14px">गरीबी और बेरोज़गारी<br>से मुकाबला</div></div>
${pres(1.2, -104, 900)}${cap('f2')}`, this.css);
  },
  f3() {
    const pins = `let h='';for(const k in ${JSON.stringify(NAMES)}){const [x,y]=PT(k);const n=${JSON.stringify(NAMES)}[k];const side={afghanistan:[16,-74],pakistan:[-90,30],india:[28,-26],nepal:[-90,-80],bhutan:[-20,-80],bangladesh:[26,6],srilanka:[30,-22],maldives:[30,-22]}[k];
h+='<svg class="ab" style="left:'+(x-16)+'px;top:'+(y-40)+'px" width="32" height="44" viewBox="0 0 32 44"><path d="M16 42 C16 30 4 24 4 14 A12 12 0 1 1 28 14 C28 24 16 30 16 42 Z" fill="#8c2f24" stroke="#2c241a" stroke-width="2"/><circle cx="16" cy="14" r="5" fill="#f2e8d2"/></svg>';
h+='<div class="ab lab" style="left:'+(x+side[0])+'px;top:'+(y+side[1])+'px">'+n+'</div>';}document.getElementById('pins').innerHTML=h;`;
    return page(this.map(pins, false) + `<div id="pins"></div>
<div class="ab" style="left:0;right:0;top:70px;text-align:center"><div class="rib" style="font-size:70px">सार्क के सदस्य देश · <span style="font-family:Rozha;color:#8c2f24">8</span></div></div>${cap('f3')}`, this.css);
  },
};

const OPTS = { A, B, C, D };
const out = path.join(HERE, 'out');
fs.mkdirSync(out, { recursive: true });
for (const [k, o] of Object.entries(OPTS)) for (const f of ['f1', 'f2', 'f3']) {
  const dir = path.join(out, `.${k}${f}`);
  const [file] = await renderStills({ html: o[f](), outDir: dir, times: [0], layers: ['preview'], size: [1080, 1920], log: () => { } });
  fs.renameSync(file, path.join(out, `${k}_${f}.png`)); fs.rmSync(dir, { recursive: true, force: true });
  console.log(`${k}_${f}`);
}
