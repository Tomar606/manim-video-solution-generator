// Storyboard sketch: three rough frames of the blueprint look. Not the kit.
//   node work/geo-c3-sa-01/board/sketch/sketch.mjs
import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module';
const ROOT = process.cwd(), D = path.join(ROOT, 'work/geo-c3-sa-01/board/sketch');
const require = createRequire(path.join(ROOT, 'tools/clip/package.json'));
const { chromium } = require('playwright');
const b64 = (f, m) => `data:${m};base64,` + fs.readFileSync(f).toString('base64');
const font = f => b64(path.join(ROOT, f), 'font/ttf');
const BG = b64(path.join(D, 'bg_toned.png'), 'image/png'), HIM = b64(path.join(D, 'him.png'), 'image/png');
const CLIP = b64(path.join(D, 'stand_in.jpg'), 'image/jpeg');
const Y = '#ffd54a', R = '#ff6a4d', C = '#9cc4ec';

const css = `
@font-face{font-family:B;src:url(${font('docs/history-poc/fonts/ttf/Baloo2[wght].ttf')})}
@font-face{font-family:Ka;src:url(${font('assets/fonts/Kalam-Regular.ttf')})}
@font-face{font-family:H;src:url(${font('docs/history-poc/fonts/ttf/Hind-Bold.ttf')})}
*{margin:0;box-sizing:border-box}
.f{position:relative;width:1080px;height:1920px;overflow:hidden;background:#0f3a68 url(${BG}) center/cover;color:#fff;font-family:B;font-weight:800}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.07) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.07) 2px,transparent 2px);background-size:60px 60px}
.pool{position:absolute;width:1100px;height:900px;left:-10px;border-radius:50%;background:radial-gradient(closest-side,rgba(156,196,236,.42),rgba(156,196,236,0))}
.him{position:absolute;transform-origin:0 0}
.cap{position:absolute;left:64px;right:64px;top:1700px;height:120px;border:3px solid rgba(255,255,255,.85);background:rgba(10,36,66,.88);display:flex;align-items:center;justify-content:center;gap:18px;font:52px H;color:${C}}
.cap::after{content:'';position:absolute;right:-3px;bottom:-3px;width:110px;height:40px;border-left:3px solid rgba(255,255,255,.85);border-top:3px solid rgba(255,255,255,.85)}
.cap .on{color:#fff}.cap .now{color:#fff;border-bottom:5px solid #fff}
.eb{position:absolute;left:64px;top:70px;display:flex;align-items:center;gap:24px;font:800 46px B;color:${C}}
.t{position:absolute;white-space:nowrap}
.k{font-family:Ka;font-weight:400}
`;
const him = (s, x0, y0) => `<div class="pool" style="top:${y0 - 120}px;transform:scale(${s / .82});transform-origin:50% 100%"></div><img class="him" src="${HIM}" style="left:${x0}px;top:${y0}px;transform:scale(${s})">`;
const cap = ws => `<div class="cap">${ws.map(([w, c]) => `<span class="${c || ''}">${w}</span>`).join('')}</div>`;

// the building: roof + n pillars + plinth, inside (x,y,w,h)
function building({ x, y, w, h, lit = [1, 2, 3, 4], glow = 0, q = false, title = true, roofSize = 64 }) {
  const roofH = h * .2, plH = h * .07, py0 = y + roofH + 12, py1 = y + h - plH;
  const pw = w * .11, gap = (w - 4 * pw) / 5;
  let s = `<svg class="t" style="left:0;top:0" width="1080" height="1920" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round">`;
  s += `<path d="M${x - 20} ${y + roofH} L${x + w / 2} ${y} L${x + w + 20} ${y + roofH} Z" fill="rgba(15,58,104,.55)"/>`;
  if (title) s += `<text x="${x + w / 2}" y="${y + roofH - 26}" fill="${Y}" stroke="none" font-family="B" font-weight="800" font-size="${roofSize}" text-anchor="middle">मानव विकास</text>`;
  s += `<rect x="${x - 10}" y="${y + roofH}" width="${w + 20}" height="12" fill="#fff"/>`;
  for (let i = 0; i < 4; i++) {
    const px = x + gap + i * (pw + gap), on = lit.includes(i + 1);
    s += `<rect x="${px - 10}" y="${py0}" width="${pw + 20}" height="22" ${on ? '' : 'stroke-dasharray="10 10"'} />`;
    s += `<rect x="${px}" y="${py0 + 22}" width="${pw}" height="${py1 - py0 - 22}" ${on ? `fill="rgba(255,255,255,${glow === i + 1 ? .35 : .08})"` : 'stroke-dasharray="14 12" stroke-opacity=".55"'} ${glow === i + 1 ? 'stroke="' + Y + '" stroke-width="7"' : ''}/>`;
    for (let k = 1; k < 3; k++) s += `<line x1="${px + pw * k / 3}" y1="${py0 + 30}" x2="${px + pw * k / 3}" y2="${py1 - 8}" stroke-width="2" stroke-opacity=".5"/>`;
    s += `<circle cx="${px + pw / 2}" cy="${py0 + 64}" r="${pw * .32}" fill="#0f3a68" ${glow === i + 1 ? 'stroke="' + Y + '"' : ''}/>`;
    s += `<text x="${px + pw / 2}" y="${py0 + 64 + pw * .14}" fill="${glow === i + 1 ? Y : '#fff'}" stroke="none" font-family="B" font-weight="800" font-size="${pw * .42}" text-anchor="middle">${q && !lit.includes(i + 1) ? '?' : i + 1}</text>`;
  }
  s += `<rect x="${x - 30}" y="${py1}" width="${w + 60}" height="${plH}" fill="rgba(15,58,104,.55)"/><line x1="${x - 60}" y1="${py1 + plH}" x2="${x + w + 60}" y2="${py1 + plH}"/>`;
  for (let i = 0; i < 14; i++) s += `<line x1="${x - 50 + i * (w + 100) / 14}" y1="${py1 + plH}" x2="${x - 70 + i * (w + 100) / 14}" y2="${py1 + plH + 20}" stroke-width="3"/>`;
  return s + '</svg>';
}
const NAMES = ['समता', 'सतत पोषणीयता', 'उत्पादकता', 'सशक्तीकरण'];
const MEAN = ['अवसरों तक सबकी समान पहुँच', 'हर पीढ़ी को समान अवसर', 'मानव श्रम की उत्पादकता, क्षमताओं के निर्माण से', 'अपने विकल्प चुनने की शक्ति'];
const bullet = (n, x, y, sz = 64) => `<div class="t" style="left:${x}px;top:${y}px;width:${sz}px;height:${sz}px;border:4px solid #fff;border-radius:50%;font-size:${sz * .62}px;line-height:${sz - 4}px;text-align:center">${n}</div>`;

// A: scene 6, the four names
const A = `<div class="f"><div class="grid"></div>
${building({ x: 150, y: 150, w: 780, h: 560, lit: [1, 2, 3, 4] })}
<div class="t" style="left:64px;top:760px;font:800 34px B;color:${C};letter-spacing:.06em">चार घटक ───────────────────────────</div>
${NAMES.map((n, i) => bullet(i + 1, 64, 830 + i * 86) + `<div class="t" style="left:156px;top:${822 + i * 86}px;font-size:64px;color:${Y}">${n}</div>`).join('')}
${him(.82, 100, 1170)}
${cap([['उत्पादकता', 'on'], ['और', 'on'], ['सशक्तीकरण', 'now'], ['इन्हें'], ['याद'], ['रखो']])}</div>`;

// B: scene 13, two axes
const fig = (x, y, s = 1, c = '#fff', fill = 'rgba(15,58,104,.6)') => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${c}" stroke-width="5" fill="${fill}"><circle cx="0" cy="-58" r="20"/><path d="M-30 30 Q-30 -30 0 -32 Q30 -30 30 30 Z"/></g>`;
const row = (y, n = 5, s = 1, c = '#fff') => Array.from({ length: n }, (_, i) => fig(250 + i * 150, y, s, c)).join('');
const Bf = `<div class="f"><div class="grid"></div>
<div class="eb"><svg width="96" height="80" stroke="#fff" stroke-width="4" fill="none"><path d="M4 22 L48 4 L92 22 Z"/>${[0, 1, 2, 3].map(i => `<rect x="${12 + i * 20}" y="26" width="10" height="44" ${i === 1 ? `fill="${Y}" stroke="${Y}"` : i === 0 ? 'fill="#fff"' : 'stroke-dasharray="5 5"'}/>`).join('')}<line x1="2" y1="74" x2="94" y2="74"/></svg>घटक 2 / 4 · सतत पोषणीयता</div>
<svg class="t" style="left:0;top:0" width="1080" height="1920" fill="none" stroke="#fff" stroke-width="5">
<text x="64" y="290" fill="#fff" stroke="none" font-family="Ka" font-size="46">आज के सभी लोग</text>
${row(430)}
<line x1="200" y1="500" x2="900" y2="500"/><path d="M200 500 l26 -14 v28 Z M900 500 l-26 -14 v28 Z" fill="#fff"/><line x1="200" y1="470" x2="200" y2="530"/><line x1="900" y1="470" x2="900" y2="530"/>
<text x="540" y="580" fill="${Y}" stroke="none" font-family="B" font-weight="800" font-size="66" text-anchor="middle">समता ↔</text>
<text x="540" y="636" fill="#fff" stroke="none" font-family="Ka" font-size="44" text-anchor="middle">आज के सभी लोगों के बीच बराबरी</text>
${row(900, 5, .8)}
<text x="64" y="1000" fill="#fff" stroke="none" font-family="Ka" font-size="46">आने वाली पीढ़ी</text>
<line x1="980" y1="400" x2="980" y2="900"/><path d="M980 400 l-14 26 h28 Z M980 900 l-14 -26 h28 Z" fill="#fff"/><line x1="950" y1="400" x2="1010" y2="400"/><line x1="950" y1="900" x2="1010" y2="900"/>
<text x="960" y="1080" fill="${Y}" stroke="none" font-family="B" font-weight="800" font-size="62" text-anchor="end">सतत पोषणीयता ↕</text>
<text x="960" y="1136" fill="#fff" stroke="none" font-family="Ka" font-size="42" text-anchor="end">आज की और आने वाली पीढ़ी के बीच</text>
</svg>
${him(.82, 100, 1170)}
${cap([['आज', 'on'], ['की', 'on'], ['और', 'on'], ['आने', 'now'], ['वाली'], ['पीढ़ी'], ['के'], ['बीच']])}</div>`;

// C: recap, small presenter
const C3 = `<div class="f"><div class="grid"></div>
${building({ x: 210, y: 120, w: 660, h: 440, lit: [1, 2, 3, 4], glow: 4, roofSize: 56 })}
${NAMES.map((n, i) => `<div class="t" style="left:64px;top:${620 + i * 190}px;width:952px;height:166px;border:3px solid rgba(255,255,255,${i === 3 ? .95 : .45});background:rgba(10,36,66,.55)"></div>` + bullet(i + 1, 88, 646 + i * 190, 60) +
  `<div class="t" style="left:172px;top:${634 + i * 190}px;font-size:60px;color:${Y}">${n}</div><div class="t k" style="left:172px;top:${708 + i * 190}px;font-size:${i === 2 ? 38 : 44}px">— ${MEAN[i]}</div>` +
  `<div class="t" style="left:${1016 - 24 - 170}px;top:${644 + i * 190}px;width:170px;height:118px;border:3px solid #fff;background:url(${CLIP}) center/cover;${i === 2 ? 'display:none' : ''}"></div>`).join('')}
${him(.52, 261, 1440)}
${cap([['और', 'on'], ['चौथा,', 'on'], ['सशक्तीकरण', 'on'], ['यानी', 'on'], ['अपने', 'now'], ['विकल्प'], ['चुनने'], ['की'], ['शक्ति']])}</div>`;

const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
for (const [n, h] of [['A', A], ['B', Bf], ['C', C3]]) {
  await p.setContent(`<html><head><style>${css}</style></head><body>${h}</body></html>`);
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: path.join(D, `frame_${n}.png`) });
}
await b.close();
