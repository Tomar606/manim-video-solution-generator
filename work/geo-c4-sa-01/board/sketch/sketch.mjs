// Rough style frames for the storyboard (not the build): three moments in the
// proposed look "रैंच का नक्शा". Grass is a flat stand-in where a Veo clip goes.
//   node work/geo-c4-sa-01/board/sketch/sketch.mjs  -> board/sketch/frame_<t>.png
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { capture } from '../../../../tools/reel/capture.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../../../..');
const b64 = f => fs.readFileSync(path.join(ROOT, f)).toString('base64');
const font = (name, f) => `@font-face{font-family:${name};src:url(data:font/ttf;base64,${b64(f)})}`;
const him = fs.existsSync(path.join(HERE, 'him.png')) ? 'data:image/png;base64,' + fs.readFileSync(path.join(HERE, 'him.png')).toString('base64') : '';

const C = { chalk: '#f4f1e8', lime: '#c6f04a', coral: '#ff6b4a', field: '#0f2418', straw: '#c9a75e', grass: '#4f7a34', grass2: '#5d8a3c' };

// the progress strip: परिभाषा + three features, each with its legend symbol
const strip = (lit, done = []) => {
  const names = ['परिभाषा', '1', '2', '3'];
  return `<div class="strip">${names.map((n, i) => `<div class="seg ${i === lit ? 'lit' : ''} ${done.includes(i) ? 'done' : ''}"></div>`).join('')}</div>`;
};
const eyebrow = t => `<div class="eyebrow">${t}</div>`;

// a fenced plan: rows x cols parcels inside (x,y,w,h); parcel fills by index
function plan({ x, y, w, h, rows = 2, cols = 3, fill = {}, sheep = null, num = true }) {
  const pw = w / cols, ph = h / rows;
  let s = '';
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const i = r * cols + c, f = fill[i] || C.grass2;
    s += `<rect x="${x + c * pw}" y="${y + r * ph}" width="${pw}" height="${ph}" fill="${f}" opacity="0.55"/>`;
    if (num) s += `<circle cx="${x + c * pw + 46}" cy="${y + r * ph + 46}" r="26" fill="${C.field}" stroke="${C.chalk}" stroke-width="3"/><text x="${x + c * pw + 46}" y="${y + r * ph + 57}" class="pn">${i + 1}</text>`;
  }
  // fences: outer + inner lines, posts every 44 px
  const lines = [[x, y, x + w, y], [x, y + h, x + w, y + h], [x, y, x, y + h], [x + w, y, x + w, y + h]];
  for (let c = 1; c < cols; c++) lines.push([x + c * pw, y, x + c * pw, y + h]);
  for (let r = 1; r < rows; r++) lines.push([x, y + r * ph, x + w, y + r * ph]);
  for (const [a, b2, c2, d] of lines) {
    s += `<line x1="${a}" y1="${b2}" x2="${c2}" y2="${d}" stroke="${C.chalk}" stroke-width="5"/>`;
    const L = Math.hypot(c2 - a, d - b2), n = Math.floor(L / 44);
    for (let k = 0; k <= n; k++) { const px = a + (c2 - a) * k / n, py = b2 + (d - b2) * k / n; s += `<rect x="${px - 6}" y="${py - 6}" width="12" height="12" fill="${C.chalk}"/>`; }
  }
  if (sheep) {
    let seed = 7; const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
    for (let k = 0; k < sheep.n; k++) s += `<ellipse cx="${sheep.x + rnd() * sheep.w}" cy="${sheep.y + rnd() * sheep.h}" rx="11" ry="8" fill="#fff"/>`;
  }
  return s;
}

const frames = [
  // 0 — EXPLAINING, part 1 ~1:40: rotational grazing on the plan, in the board above him
  () => `
  <div class="bg" style="background:linear-gradient(160deg,#2c4a24,#1d3318)"></div>
  ${strip(1, [0])}${eyebrow('विशेषता 1 · स्थायी रैंच')}
  <div class="board">
    <div class="veo">Veo: घास, सीधे ऊपर से</div>
    <svg width="952" height="960" viewBox="64 190 952 960" style="position:absolute;left:0;top:0">
      ${plan({ x: 110, y: 260, w: 860, h: 640, fill: { 0: C.straw }, sheep: { n: 26, x: 420, y: 330, w: 230, h: 200 } })}
      <path d="M 300 420 C 380 400, 420 400, 470 420" stroke="${C.lime}" stroke-width="8" fill="none" marker-end="url(#ar)"/>
      <defs><marker id="ar" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 z" fill="${C.lime}"/></marker></defs>
    </svg>
    <div class="tag" style="left:70px;top:740px">भूखंड 1 · घास चर ली</div>
    <div class="tag lime" style="left:470px;top:740px">→ दूसरे भूखंड में</div>
  </div>
  ${him ? `<img class="him explain" src="${him}">` : ''}
  <div class="cap">तो पशुओं को <span class="now">दूसरे</span> भूखंड में ले जाया जाता है,</div>`,

  // 1 — HIDDEN, part 2: carrying capacity — two parcels side by side, then the line to write
  () => `
  <div class="bg" style="background:linear-gradient(160deg,#2c4a24,#1d3318)"></div>
  ${strip(2, [0, 1])}${eyebrow('विशेषता 2 · वहन क्षमता')}
  <div class="slip" style="left:64px;top:190px;width:952px">वहन क्षमता = चारागाह बिना खराब हुए कितने पशुओं का बोझ उठा सकता है</div>
  <svg width="1080" height="1920" style="position:absolute;left:0;top:0">
    ${plan({ x: 64, y: 420, w: 440, h: 520, rows: 1, cols: 1, num: false, fill: { 0: '#9a7a4a' }, sheep: { n: 46, x: 90, y: 450, w: 390, h: 460 } })}
    ${plan({ x: 576, y: 420, w: 440, h: 520, rows: 1, cols: 1, num: false, fill: { 0: C.grass }, sheep: { n: 12, x: 610, y: 470, w: 370, h: 420 } })}
  </svg>
  <div class="verdict coral" style="left:64px;top:968px;width:440px">ज़्यादा भेड़ें → बंजर</div>
  <div class="verdict lime" style="left:576px;top:968px;width:440px">क्षमता के अनुसार</div>
  <div class="exam" style="left:110px;top:1130px;width:860px">जितनी घास, उतने ही पशु।</div>
  <div class="cap">इसे एक लाइन में याद रखो, <span class="now">जितनी</span> घास, उतने ही पशु।</div>`,

  // 2 — TO YOU, part 1 ~1:00: the one-line difference, two columns above him
  () => `
  <div class="bg" style="background:linear-gradient(160deg,#2c4a24,#1d3318);filter:blur(0)"></div>
  <div class="dim">Veo V2 पीछे, धुंधला</div>
  ${strip(0)}${eyebrow('परिभाषा · फर्क एक लाइन में')}
  <div class="col" style="left:64px">
    <div class="ch">चलवासी</div>
    <svg width="440" height="230"><path d="M 30 190 C 90 40, 160 210, 230 90 S 360 30, 410 170" stroke="${C.chalk}" stroke-width="6" stroke-dasharray="14 12" fill="none"/><circle cx="410" cy="170" r="12" fill="${C.chalk}"/></svg>
    <div class="row">पशुओं के साथ घूमता है</div>
  </div>
  <div class="col" style="left:576px">
    <div class="ch lime">वाणिज्य</div>
    <svg width="440" height="230" viewBox="0 0 440 230">${plan({ x: 70, y: 20, w: 300, h: 190, rows: 1, cols: 2, num: false })}</svg>
    <div class="row">एक जगह टिककर</div>
    <div class="row">अधिक पूँजी</div>
    <div class="row">व्यापार के लिए</div>
  </div>
  ${him ? `<img class="him you" src="${him}">` : ''}
  <div class="cap">जबकि वाणिज्य पशुपालन <span class="now">एक</span> जगह टिककर,</div>`,
];

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
${font('Raj', 'assets/fonts/Rajdhani-Bold.ttf')}${font('Hind', 'assets/fonts/Hind-SemiBold.ttf')}${font('Kalam', 'assets/fonts/Kalam-Regular.ttf')}
*{margin:0;box-sizing:border-box}
body{width:1080px;height:1920px;overflow:hidden;background:${C.field};font-family:Hind;color:${C.chalk}}
#f{position:absolute;inset:0}
.bg{position:absolute;inset:0}
.dim{position:absolute;left:64px;top:1000px;font:32px Hind;opacity:.5}
.strip{position:absolute;left:64px;top:38px;width:952px;display:flex;gap:14px}
.seg{flex:1;height:12px;border-radius:6px;background:rgba(244,241,232,.25)}
.seg.done{background:${C.chalk}}.seg.lit{background:${C.lime};box-shadow:0 0 14px ${C.lime}}
.eyebrow{position:absolute;left:64px;top:72px;font:44px Raj;letter-spacing:1px;color:${C.lime}}
.board{position:absolute;left:64px;top:190px;width:952px;height:1060px;border:6px solid ${C.chalk};border-radius:24px;overflow:hidden;background:linear-gradient(170deg,#55803a,#3d652b)}
.veo{position:absolute;right:24px;bottom:18px;font:30px Hind;opacity:.6}
.pn{font:34px Raj;fill:${C.chalk};text-anchor:middle}
.tag{position:absolute;padding:10px 24px;border-radius:12px;background:${C.field};font:42px Hind;border:3px solid ${C.chalk}}
.tag.lime{border-color:${C.lime};color:${C.lime}}
.slip{position:absolute;padding:24px 28px;border-radius:14px;background:${C.chalk};color:${C.field};font:44px Hind;line-height:1.35}
.verdict{position:absolute;text-align:center;font:46px Raj;padding:12px 0;border-radius:12px;background:${C.field}}
.verdict.coral{color:${C.coral};border:3px solid ${C.coral}}.verdict.lime{color:${C.lime};border:3px solid ${C.lime}}
.exam{position:absolute;padding:30px 40px;background:#fbf8ef;color:#1b2a5a;font:70px Kalam;text-align:center;border-radius:6px;
 background-image:repeating-linear-gradient(#fbf8ef 0 66px,#b9c7e6 66px 68px);box-shadow:0 10px 30px rgba(0,0,0,.4);transform:rotate(-1.2deg)}
.col{position:absolute;top:190px;width:440px}
.ch{font:64px Raj;margin-bottom:10px}.ch.lime{color:${C.lime}}
.row{margin-top:20px;padding:14px 24px;border-radius:12px;background:rgba(15,36,24,.85);font:42px Hind;border-left:8px solid ${C.chalk}}
.him{position:absolute}
.him.explain{width:${1120 * 0.82}px;left:100px;top:1140px}
.him.you{width:${1120 * 1.2}px;left:-104px;top:860px}
.cap{position:absolute;left:0;right:0;top:1712px;text-align:center;font:56px Hind;color:#fff;text-shadow:0 3px 10px rgba(0,0,0,.8)}
.now{background:${C.lime};color:${C.field};border-radius:12px;padding:0 12px}
</style></head><body><div id="f"></div><script>
const F=${JSON.stringify(frames.map(f => f()))};
window.READY=document.fonts.ready;
window.frame=t=>{document.getElementById('f').innerHTML=F[Math.round(t)];return document.fonts.ready};
</script></body></html>`;

await capture({ html, stills: [0, 1, 2], out: HERE, name: 'frame' });
