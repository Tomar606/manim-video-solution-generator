// "One line" captions for a reel: a single line at the bottom of the frame
// carrying a short phrase of the sentence; the word being spoken RIGHT NOW is
// marked, words already spoken are plain, words still to come are dimmed. Each
// phrase fades up over 0.15 s.
//
//   node tools/reel/captions_line.mjs <slug> <part>          -> work/<slug>/out/layers/p<N>/captions.mov
//                                                               work/<slug>/out/layers/p<N>/caption_phrases.json
//   node tools/reel/captions_line.mjs <slug> <part> --dry    -> the json only, no render
//   node tools/reel/captions_line.mjs <slug> <part> --check [t1,t2,...]
//        -> .../p<N>/captions_check.png: the line over frames of the clip (12 by default)
//
// TEXT + CLOCK  work/<slug>/asr/aligned_part<N>.json, written by tools/reel/words.mjs:
//        the words in the spelling the screen shows, already on the voice's clock.
//        Nothing is aligned or re-timed here.
// SKIN   work/<slug>/design/captions.json: { style: {...}, keep: ["a|b", ...] }.
//        `style` overrides DEFAULT_STYLE below key by key; `keep` (and post, tail,
//        dangle, opener) ADD to the word lists the phrase splitter uses.
// WIDTH  measured in Chromium itself, before the split, so a phrase is never
//        wider than the line: it shrinks to min_size at most, and a phrase that
//        would need less is split differently instead. Never two lines.
//
// Grown out of work/geo-c2-la-01/design/captions_line.mjs (which stays where it
// is). The splitter is that file's, unchanged. What is new is the skin: a paper
// `strip` behind the line and a marker `underline` under the spoken word, both
// off unless the video's captions.json asks for them.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { renderLayers, renderStills } from './layers.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const abs = f => (path.isAbsolute(f) ? f : path.join(ROOT, f));

// ---- the style -----------------------------------------------------------------
const DEFAULT_STYLE = {
  font: 'docs/history-poc/fonts/ttf/Mukta-ExtraBold.ttf',
  size: 52, min_size: 40,           // px; a phrase shrinks to fit, never below min
  color: '#fff',
  stroke: 8, stroke_color: '#000',  // px outline, paint-order stroke fill; 0 = none
  shadow: 4,                        // px hard drop shadow under the letters; 0 = none
  centre_y: 1775, x0: 60, x1: 1020, // the line's centre and its horizontal limits
  gap_em: 0.34,                     // space between words
  text_dy: 0,                       // px, nudges the letters inside the line (negative = up)
  active: { color: null, scale: 1, stroke: null },// the spoken word: its colour (null = unchanged), growth, and its outline
                                    // (null = the line's; e.g. "0px transparent" when an underline block sits behind it)
  upcoming_opacity: 0.55,
  fade_up: 0.15, hold_after_last_word: 0.6,
  max_words: 7,
  strip: null,                      // a band behind the line, as wide as the phrase; see STRIP
  underline: null,                  // a stroke under the spoken word; see UNDERLINE
  check_paper: null,                // --check: every last tile of a row sits on this flat colour instead of the clip
};
const STRIP = {
  fill: '#fff', height: 104, pad_x: 34, // px; the strip is the phrase plus pad_x each side
  torn: 0,                          // px the two ends are torn in by; 0 = cut straight
  edge: null,                       // colour of a hairline round the strip (follows the tear)
  shadow: null,                     // "x y blur colour" of a soft shadow under it
};
const UNDERLINE = {
  color: '#f00', top_em: 0.9, thickness_em: 0.17, // where it sits in the word's 1 em box
  overhang: 4,                      // px it runs past the word on each side
  slant: -1.2,                      // degrees
  wipe: 0.12,                       // s, left to right
};
const merge = (a, b) => {
  const o = { ...a };
  for (const [k, v] of Object.entries(b || {})) {
    if (k.startsWith('_')) continue;
    o[k] = v && typeof v === 'object' && !Array.isArray(v) && a[k] && typeof a[k] === 'object' ? merge(a[k], v) : v;
  }
  return o;
};

// ---- the wording -----------------------------------------------------------------
// never the first word of a phrase cut out of the middle of a clause
const POST = new Set(['के', 'की', 'का', 'में', 'से', 'को', 'पर', 'है', 'हैं', 'भी', 'ही', 'तक']);
// reads badly as the first word of such a phrase (the tail of a verb or of "के लिए")
const TAIL = new Set(['था', 'थी', 'थे', 'ने', 'होता', 'होती', 'होते', 'होगा', 'जाता', 'जाती', 'जाते', 'जाएगा', 'गया', 'गई', 'चुका',
  'लेते', 'करते', 'करता', 'करती', 'करने', 'करना', 'होने', 'होना', 'जाने', 'जाना', 'सकते', 'रहते', 'वाले', 'वाली', 'चाहिए', 'कीजिए', 'लिए', 'साथ', 'साथ-साथ', 'बाद', 'नहीं', 'देती']);
// reads badly as the LAST word of such a phrase (it belongs to what follows)
const DANGLE = new Set(['और', 'या', 'एवं', 'तथा', 'कि', 'तो', 'अब', 'जहाँ', 'वहाँ', 'क्योंकि', 'इसलिए', 'इसीलिए', 'जबकि',
  'एक', 'ये', 'यह', 'इस', 'उन', 'सबसे', 'बहुत', 'कई', 'हम']);
// pairs that stay on one line; a video adds its own in captions.json
const KEEP = new Set(['Board|Exam', 'MP|Board', 'दूर-दूर|तक', 'कौन-कौन|से', 'Part|1', 'Part|2', 'Part|3']);
// a clause opens on these: after a comma they want a line of their own
const OPENER = new Set(['जबकि', 'क्योंकि', 'इसलिए', 'इसीलिए', 'लेकिन', 'पर', 'तो', 'कि', 'अब', 'यानी']);

// ---- arguments ---------------------------------------------------------------------
const [SLUG, PARTARG, FLAG, ARG1] = process.argv.slice(2);
const PN = +(PARTARG || '').replace(/^p(art)?/i, '');
if (!SLUG || !PN || (FLAG && !['--dry', '--check'].includes(FLAG))) {
  console.error('usage: captions_line.mjs <slug> <part> [--dry | --check [t1,t2,..]]'); process.exit(2);
}
const WORK = path.join(ROOT, 'work', SLUG);
const inputs = JSON.parse(fs.readFileSync(path.join(WORK, 'inputs.json'), 'utf8'));
// the video's frame rate (look.json "fps"; 30 unless the video says otherwise, GEO-C3-SA-01 runs at its clip's 25)
const FPS = (() => { try { return JSON.parse(fs.readFileSync(path.join(WORK, 'look.json'), 'utf8')).fps || 30; } catch { return 30; } })();
const INP = inputs.parts.find(p => p.part === PN);
if (!INP) { console.error(`${SLUG} has no part ${PN} in inputs.json`); process.exit(2); }
const PART = 'p' + PN, dur = INP.clip.duration;
const IN = {
  words: `work/${SLUG}/asr/aligned_part${PN}.json`,
  skin: `work/${SLUG}/design/captions.json`,
  clip: INP.clip.path,
};
const OUT = path.join(WORK, 'out/layers', PART);
fs.mkdirSync(OUT, { recursive: true });

const SKIN = fs.existsSync(abs(IN.skin)) ? JSON.parse(fs.readFileSync(abs(IN.skin), 'utf8')) : {};
const STYLE = merge(DEFAULT_STYLE, SKIN.style);
if (STYLE.strip) STYLE.strip = { ...STRIP, ...STYLE.strip };
if (STYLE.underline) STYLE.underline = { ...UNDERLINE, ...STYLE.underline };
for (const [name, set] of [['keep', KEEP], ['post', POST], ['tail', TAIL], ['dangle', DANGLE], ['opener', OPENER]])
  for (const x of SKIN[name] || []) set.add(x);
const SP = STYLE.strip, UL = STYLE.underline;
const GROWS = STYLE.active.scale > 1;
// usable text width: the limits, less whatever stands between them and the letters
const MAXW = STYLE.x1 - STYLE.x0 - (SP ? 2 * SP.pad_x : 0) - STYLE.stroke - (GROWS ? 16 : 0);

// ---- caption words, already on the clock ---------------------------------------------
const CLAUSE = /[।,—–?!]$/, SENTENCE = /[।?!]$/, PUNCT = /[—–,.!?।…'"‘’“”:;()]/g;
const bare = w => w.replace(PUNCT, '');
const aligned = JSON.parse(fs.readFileSync(abs(IN.words), 'utf8'));
if (Math.abs(aligned.dur - dur) > 0.05) console.error(`warning: ${IN.words} was aligned to ${aligned.dur} s, the clip is ${dur} s`);
const A = aligned.words.map(w => ({ w: w.w, s: w.s, e: w.e, src: w.src }));

// ---- page ------------------------------------------------------------------------------
const TEAR_R = [0.55, 0, 0.9, 0.25, 1, 0.4, 0.1], TEAR_L = [0.2, 0.85, 0, 0.6, 0.15, 1, 0.45];
function tornPath(px) {
  if (!px) return '';
  const n = TEAR_R.length - 1, pts = [];
  TEAR_R.forEach((v, k) => pts.push(`calc(100% - ${(v * px).toFixed(1)}px) ${(100 * k / n).toFixed(1)}%`));
  TEAR_L.forEach((v, k) => pts.push(`${(v * px).toFixed(1)}px ${(100 * (n - k) / n).toFixed(1)}%`));
  return `clip-path:polygon(${pts.join(',')});`;
}
const stripFilter = SP ? [SP.edge && `drop-shadow(0 0 0.6px ${SP.edge}) drop-shadow(0 0 0.6px ${SP.edge})`, SP.shadow && `drop-shadow(${SP.shadow})`].filter(Boolean).join(' ') : '';
// Only the band the line lives in is drawn (y0, h); the rest of the frame is empty and is put back afterwards.
const css = (y0 = 0, h = 1920) => `
@font-face{font-family:Cap;src:url(data:font/ttf;base64,${fs.readFileSync(abs(STYLE.font)).toString('base64')})}
html,body{margin:0;background:transparent}
#st{position:relative;width:1080px;height:${h}px;overflow:hidden}
#cap{position:absolute;left:${STYLE.x0}px;width:${STYLE.x1 - STYLE.x0}px;top:${STYLE.centre_y - y0}px;height:0;display:flex;align-items:center;justify-content:center}
#strip{position:relative;flex:none;display:flex;align-items:center;justify-content:center;opacity:0;${SP ? `height:${SP.height}px;` : ''}${stripFilter ? `filter:${stripFilter};` : ''}}
#paper{position:absolute;inset:0;${SP ? `background:${SP.fill};${tornPath(SP.torn)}` : ''}}
#clip{position:absolute;inset:0;overflow:hidden;display:flex;align-items:center;justify-content:center}
#box{position:relative;flex:none;font-family:Cap;font-size:${STYLE.size}px;line-height:1;color:${STYLE.color};white-space:nowrap;isolation:isolate;
  ${STYLE.stroke ? `-webkit-text-stroke:${STYLE.stroke}px ${STYLE.stroke_color};paint-order:stroke fill;` : ''}${STYLE.shadow ? `text-shadow:0 ${STYLE.shadow}px 0 ${STYLE.stroke_color};` : ''}}
#box span{display:inline-block;position:relative;margin:0 ${STYLE.gap_em / 2}em;transform-origin:50% 58%}
${UL ? `#box span i{position:absolute;z-index:-1;left:-${UL.overhang}px;right:-${UL.overhang}px;top:${UL.top_em}em;height:${UL.thickness_em}em;background:${UL.color};
  clip-path:polygon(0% 34%,5% 8%,52% 0%,100% 10%,99% 76%,58% 100%,3% 94%);transform-origin:0 50%;display:none}` : ''}
#lab{position:absolute;left:24px;top:${1300 - y0}px;font:600 40px/1 Menlo,monospace;color:#fff;background:#000c;padding:10px 16px}`;

// Chromium's own word widths at the base size, and where the letters' body sits in the line box.
async function measure(list) {
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css()}</style></head><body>
<div id="st"><div id="cap"><div id="strip" style="opacity:1"><div id="box"></div></div></div></div></body></html>`;
  // Playwright lives in tools/clip/node_modules and nowhere else.
  const { chromium } = createRequire(path.join(ROOT, 'tools/clip/package.json'))('playwright');
  const browser = await chromium.launch();
  try {
    const pg = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    await pg.setContent(html, { waitUntil: 'load' });
    return await pg.evaluate(async ({ L, size }) => {
      await document.fonts.load(size + 'px Cap', 'कमल Aa 12');
      const box = document.getElementById('box'), w = {};
      const ok = document.fonts.check(size + 'px Cap');
      for (const t of L) { box.innerHTML = '<span style="padding:0;margin:0"></span>'; box.firstChild.textContent = t; w[t] = box.firstChild.getBoundingClientRect().width; }
      box.innerHTML = '<span style="padding:0;margin:0">कमल<b style="display:inline-block;width:0;height:0"></b></span>';
      const r = box.firstChild.getBoundingClientRect(), base = box.querySelector('b').getBoundingClientRect().bottom - r.top;
      const cx = document.createElement('canvas').getContext('2d'); cx.font = size + 'px Cap'; const m = cx.measureText('कमल');
      const dy = r.height / 2 - (base - m.actualBoundingBoxAscent / 2);
      return { ok, w, dy };
    }, { L: list, size: STYLE.size });
  } finally { await browser.close(); }
}
const M = await measure([...new Set(A.map(a => a.w))]);
if (!M.ok) throw new Error(`${STYLE.font} did not load in the measuring pass`);
A.forEach(a => { a.width = M.w[a.w]; });
const GAP = STYLE.gap_em * STYLE.size;
const widthOf = (a, b) => A.slice(a, b).reduce((s, x) => s + x.width, 0) + (b - a - 1) * GAP;
// widest text the line takes at this size (the outline does not scale with the font)
const sizeFor = w => (w <= MAXW ? STYLE.size : Math.floor(STYLE.size * MAXW / w));

// ---- phrases --------------------------------------------------------------------------------
// Punctuation first: a break after । , — ? ! is free, a phrase that swallows one
// pays for it (a comma little, a full stop a lot). Then length: 4-6 words is
// free, 7 and 3 cost a little, 2 and 1 a lot — so a two-word clause joins its
// neighbour across a comma rather than flashing alone, and so does a phrase that
// would be on screen for under a second. A break inside a clause costs, and it
// may not land before a postposition or inside a KEEP pair.
const HARD = 1000;
function cost(a, b) {
  const n = b - a;
  if (n > STYLE.max_words) return Infinity;
  let c = 1 + (n === 1 ? 4 : n === 2 ? 2.2 : n === 3 ? 0.6 : n === 7 ? 0.4 : 0);
  for (let k = a; k < b - 1; k++) c += SENTENCE.test(A[k].w) ? 6 : CLAUSE.test(A[k].w) ? (OPENER.has(bare(A[k + 1].w)) ? 2.4 : 1.6) : 0;
  const shown = (b < A.length ? A[b].s : dur) - A[a].s;
  c += shown < 0.7 ? 2.5 : shown < 1 ? 1 : 0;
  if (a > 0) {
    const prev = bare(A[a - 1].w), cur = bare(A[a].w);
    if (KEEP.has(prev + '|' + cur)) c += HARD;
    if (!CLAUSE.test(A[a - 1].w)) {
      c += 0.8;
      if (POST.has(cur)) c += HARD;
      if (TAIL.has(cur)) c += 1.5;
      if (DANGLE.has(prev)) c += 1.2;
      if (POST.has(prev)) c -= 0.3;
    }
  }
  const fsz = sizeFor(widthOf(a, b));
  c += fsz < STYLE.min_size ? HARD : (STYLE.size - fsz) * 0.3;
  return c;
}
const N = A.length, best = new Array(N + 1).fill(Infinity), from = new Array(N + 1).fill(0); best[0] = 0;
for (let b = 1; b <= N; b++) for (let a = Math.max(0, b - STYLE.max_words); a < b; a++) {
  const v = best[a] + cost(a, b);
  if (v < best[b]) { best[b] = v; from[b] = a; }
}
const phrases = [];
for (let b = N; b > 0; b = from[b]) phrases.unshift({ a: from[b], b });
phrases.forEach(p => {
  p.words = A.slice(p.a, p.b);
  p.width = widthOf(p.a, p.b); p.size = sizeFor(p.width);
  p.start = p.words[0].s;
  p.last_word_end = p.words[p.words.length - 1].e;
});
phrases.forEach((p, i) => {
  const next = phrases[i + 1] ? phrases[i + 1].start : dur;
  p.end = +Math.min(dur, next - p.last_word_end > STYLE.hold_after_last_word ? p.last_word_end + STYLE.hold_after_last_word : next).toFixed(3);
  p.clears = p.end < next - 1e-6;   // the line goes empty before the next phrase
  // the strip is the phrase at its own size, plus the padding
  p.strip_w = SP ? Math.round(p.width * p.size / STYLE.size + 2 * SP.pad_x) : 0;
});
// how long each word stays lit: to the next word, unless a pause follows it
A.forEach((a, i) => { const next = A[i + 1] ? A[i + 1].s : dur; a.lit_until = +(next - a.e <= 0.3 ? next : a.e + 0.12).toFixed(3); });

// ---- audit -----------------------------------------------------------------------------------
const problems = [];
phrases.forEach((p, i) => {
  const first = bare(p.words[0].w), flags = [];
  if (p.a > 0 && !CLAUSE.test(A[p.a - 1].w) && POST.has(first)) flags.push('starts on a postposition');
  if (p.a > 0 && KEEP.has(bare(A[p.a - 1].w) + '|' + first)) flags.push('splits a keep-together pair');
  if (p.size < STYLE.min_size) flags.push('below the minimum size');
  if (p.end - p.start < 0.25) flags.push(`on screen for ${(p.end - p.start).toFixed(2)} s`);
  const by = src => p.words.filter(w => w.src === src).map(w => w.w).join(' ');
  if (by('interpolated')) flags.push('interpolated: ' + by('interpolated'));
  if (by('whisper-after-pause')) flags.push('onset moved to the end of a pause: ' + by('whisper-after-pause'));
  const other = p.words.filter(w => !['whisper', 'whisper-joined', 'interpolated', 'whisper-after-pause'].includes(w.src));
  if (other.length) flags.push('timed by ' + other.map(w => `${w.src}: ${w.w}`).join(', '));
  const brief = p.words.filter(w => w.e - w.s < 0.08 && [...bare(w.w)].length >= 4);   // a particle can be that short, a full word cannot
  if (brief.length) flags.push('under 0.08 s long: ' + brief.map(w => `${w.w} (${Math.round((w.e - w.s) * 1000)} ms)`).join(' '));
  p.flags = flags;
  if (flags.length) problems.push({ phrase: i, start: p.start, text: p.words.map(w => w.w).join(' '), flags });
});
const count = src => A.filter(w => w.src === src).length;
const audit = {
  part: PART, duration: dur, inputs: IN, style: STYLE, vertical_offset_px: +M.dy.toFixed(2),
  counts: { words: N, whisper: count('whisper'), joined: count('whisper-joined'), interpolated: count('interpolated'), after_pause: count('whisper-after-pause'),
    phrases: phrases.length, shrunk: phrases.filter(p => p.size < STYLE.size).length, cleared_lines: phrases.filter(p => p.clears).length },
  uncertain: problems,
  phrases: phrases.map((p, i) => ({
    i, start: p.start, end: p.end, text: p.words.map(w => w.w).join(' '), font_px: p.size, width_px: Math.round(p.width * p.size / STYLE.size),
    words: p.words.map(w => ({ w: w.w, s: w.s, e: w.e, src: w.src })),
  })),
};
const AUDIT = path.join(OUT, 'caption_phrases.json');
// --dry and --check rewrite this file; they keep what the last render said about itself
try { const was = JSON.parse(fs.readFileSync(AUDIT, 'utf8')).render; if (was && FLAG) audit.render = was; } catch { /* no audit yet */ }
fs.writeFileSync(AUDIT, JSON.stringify(audit, null, 1));
const c = audit.counts;
console.log(`${PART}: ${N} words (${c.whisper} matched, ${c.joined} joined, ${c.interpolated} interpolated, ${c.after_pause} moved after a pause), ` +
  `${phrases.length} phrases (${c.shrunk} shrunk, ${c.cleared_lines} clear before the next)`);
if (FLAG === '--dry') {
  for (const p of audit.phrases) console.log(`${p.start.toFixed(2).padStart(7)} ${p.end.toFixed(2).padStart(7)} ${String(p.font_px).padStart(2)}px ${String(p.width_px).padStart(4)}  ` +
    p.words.map(w => w.w + (w.src === 'interpolated' ? '*' : w.src === 'whisper' || w.src === 'whisper-joined' ? '' : '^')).join(' '));
  for (const u of problems) console.log('  ?', u.phrase, u.start, u.text, '|', u.flags.join('; '));
  process.exit(0);
}

// ---- the render page -----------------------------------------------------------------------------
// render(t) is a function of t alone: layers.mjs hands any 15 s to any page.
// pw: the width of the strip this phrase takes over from (0 = the line was empty, so the strip fades up with the words)
const DATA = phrases.map((p, i) => ({ s: p.start, e: p.end, f: p.size, o: p.clears ? 1 : 0, sw: p.strip_w,
  pw: i > 0 && !phrases[i - 1].clears ? phrases[i - 1].strip_w : 0, w: p.words.map(w => [w.w, w.s, w.lit_until]) }));
const page = (label, y0 = 0, h = 1920) => `<!doctype html><html><head><meta charset="utf-8"><style>${css(y0, h)}</style></head><body>
<div id="st">${label ? '<div id="lab"></div>' : ''}<div id="cap"><div id="strip"></div></div></div><script>
const CH=${JSON.stringify(DATA)},DY=${M.dy / STYLE.size},TDY=${STYLE.text_dy},DIM=${STYLE.upcoming_opacity},UP=${STYLE.fade_up},
  GROW=${STYLE.active.scale - 1},ACTIVE=${JSON.stringify(STYLE.active.color)},ASTROKE=${JSON.stringify(STYLE.active.stroke ?? null)},STRIP=${SP ? 1 : 0},UL=${UL ? 1 : 0},WIPE=${UL ? UL.wipe : 0},SLANT=${UL ? UL.slant : 0};
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const P=(t,a,b)=>clamp((t-a)/(b-a));
const ease=u=>1-Math.pow(1-u,3);
const q=v=>Math.round(v*20)/20;
// nothing on the page uses the font until the first phrase is built: load it before the first frame is drawn
window.READY=document.fonts.load('${STYLE.size}px Cap','कमल Aa 12');
const lab=document.getElementById('lab');
let strip=document.getElementById('strip'),box=null,cur=-1;
// a fresh element per phrase, so nothing of the last phrase survives in paint
function build(c){
  const ns=document.createElement('div');ns.id='strip';
  if(c){
    box=document.createElement('div');box.id='box';box.style.fontSize=c.f+'px';
    for(const w of c.w){const s=document.createElement('span');s.textContent=w[0];if(UL)s.appendChild(document.createElement('i'));box.appendChild(s);}
    // on a strip the words are clipped to it: while it is still widening to a longer phrase nothing hangs off its ends
    if(STRIP){const p=document.createElement('div');p.id='paper';ns.appendChild(p);const cl=document.createElement('div');cl.id='clip';cl.appendChild(box);ns.appendChild(cl);}
    else ns.appendChild(box);
  }
  strip.replaceWith(ns);strip=ns;
}
window.render=(t,layer)=>{
  if(lab)lab.textContent='t = '+t.toFixed(2)+' s';
  const i=CH.findIndex(c=>t>=c.s&&t<c.e);
  if(i<0){ if(cur!==-1){cur=-1;build(null);} return; }
  const c=CH[i];
  if(i!==cur){cur=i;build(c);}
  const u=ease(P(t,c.s,c.s+UP));
  const out=c.o?1-P(t,c.e-.1,c.e):1;
  // the strip stays on the page from one phrase to the next and only changes width; the words fade up on it
  const kept=STRIP&&c.pw>0;
  strip.style.opacity=((kept?1:u)*out).toFixed(2);
  if(STRIP)strip.style.width=(kept?c.pw+(c.sw-c.pw)*u:c.sw).toFixed(1)+'px';
  box.style.opacity=(kept?u:1).toFixed(2);
  box.style.transform='translateY('+(DY*c.f+TDY+6*(1-u)).toFixed(1)+'px)';
  const sp=box.children;
  for(let k=0;k<c.w.length;k++){
    const on=c.w[k][1],till=c.w[k][2],s=sp[k],ul=UL?s.lastChild:null;
    if(t<on){s.style.cssText='opacity:'+DIM;if(ul)ul.style.cssText='';continue;}
    const vin=q(P(t,on,on+.07)),v=Math.min(vin,q(1-P(t,till,till+.07)));
    s.style.cssText=(vin<1?'opacity:'+(DIM+(1-DIM)*vin).toFixed(2)+';':'')+
      (v>0&&ACTIVE?'color:'+ACTIVE+';':'')+(v>0&&ASTROKE?'-webkit-text-stroke:'+ASTROKE+';':'')+(v>0&&GROW?'transform:scale('+(1+GROW*v).toFixed(3)+');':'');
    if(ul)ul.style.cssText=v>0?'display:block;opacity:'+q(1-P(t,till,till+.07))+';transform:rotate('+SLANT+'deg) scaleX('+ease(P(t,on,on+WIPE)).toFixed(3)+')':'';
  }
};
</script></body></html>`;

const ff = args => { const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', ...args], { stdio: 'inherit' }); if (r.status !== 0) throw new Error('ffmpeg failed: ' + args.join(' ')); };

if (FLAG === '--check') {
  // twelve phrases spread over the part, each caught on its middle word, over the clip's own frame
  const T = ARG1 ? ARG1.split(',').map(Number) : Array.from({ length: 12 }, (_, k) => {
    const p = phrases[Math.round((k + 0.5) * phrases.length / 12 - 0.5)], w = p.words[Math.floor(p.words.length / 2)];
    return +Math.min(w.s + 0.15, p.end - 0.05).toFixed(2);
  });
  const tmp = path.join(OUT, '_check'); fs.rmSync(tmp, { recursive: true, force: true });
  try {
    const stills = await renderStills({ html: page(true), outDir: tmp, times: T, layers: ['check'], log: () => {} });
    const cols = Math.min(3, T.length), rows = Math.ceil(T.length / cols);
    T.forEach((t, k) => {
      // the clip is landscape on green: centre-crop it to the reel's frame, and keep the bottom third, for judging only
      const onPaper = STYLE.check_paper && k % cols === cols - 1;
      const back = onPaper ? ['-f', 'lavfi', '-i', `color=c=${STYLE.check_paper.replace('#', '0x')}:s=1080x1920`] : ['-ss', String(t), '-i', abs(IN.clip)];
      ff([...back, '-i', stills[k], '-frames:v', '1', '-filter_complex',
        `[0:v]scale=-2:1920,crop=1080:1920[b];[b][1:v]overlay=0:0,crop=1080:640:0:1280,scale=540:320`, path.join(tmp, `c_${String(k).padStart(2, '0')}.png`)]);
    });
    ff(['-start_number', '0', '-i', path.join(tmp, 'c_%02d.png'), '-frames:v', '1', '-vf', `tile=${cols}x${rows}`, path.join(OUT, 'captions_check.png')]);
  } finally {
    if (process.env.KEEP_CHECK) console.log('kept', tmp); else fs.rmSync(tmp, { recursive: true, force: true });
  }
  console.log('wrote', path.join(OUT, 'captions_check.png'), 'at', T.join(', '));
} else {
  const t0 = Date.now();
  // Draw the band only, then pad it back to the frame. A screenshot of the whole frame is about
  // 70 KB however little is on it (Chromium deflates for speed), so a part cost 115 MB of
  // stills and as much again for the movie while it was being made; the band costs a third.
  // The padded frames are deflated properly, and every timestamp must come out as it went in.
  const half = Math.ceil(((SP ? SP.height / 2 : STYLE.size) + 40) / 2) * 2;
  const y0 = Math.max(0, Math.round(STYLE.centre_y) - half), h = Math.min(1920 - y0, 2 * half);
  const band = path.join(OUT, '.band'), mov = path.join(OUT, 'captions.mov'), padded = path.join(OUT, 'captions.padded.mov');
  const stamps = f => spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'packet=pts,duration', '-of', 'csv=p=0', f], { encoding: 'utf8' }).stdout;
  fs.rmSync(band, { recursive: true, force: true });
  let stats;
  try {
    stats = await renderLayers({ html: page(false, y0, h), outDir: band, dur, layers: ['captions'], size: [1080, h], fps: FPS, workers: +(process.env.CAPTION_WORKERS || 3) });
    ff(['-i', path.join(band, 'captions.mov'), '-vf', `format=rgba,pad=1080:1920:0:${y0}:color=black@0`,
      '-c:v', 'png', '-compression_level', '6', '-pred', 'none', '-fps_mode', 'passthrough', '-video_track_timescale', String(FPS * 1000), padded]);
    const before = stamps(path.join(band, 'captions.mov'));
    if (!before || before !== stamps(padded)) throw new Error('padding the caption band back to the frame moved a frame');
    fs.renameSync(padded, mov);
  } finally { fs.rmSync(band, { recursive: true, force: true }); fs.rmSync(padded, { force: true }); }
  stats.captions.mb = +(fs.statSync(mov).size / 1e6).toFixed(1);
  console.log(`wrote ${mov}: ${stats.captions.written} of ${stats.captions.frames} frames, ${stats.captions.mb} MB, band y ${y0}-${y0 + h}`);
  audit.render = { ...stats.captions, seconds: +((Date.now() - t0) / 1000).toFixed(1) };
  fs.writeFileSync(AUDIT, JSON.stringify(audit, null, 1));
}
