// The words a reel SHOWS, on the clock of the voice, and a way to ask that clock
// for a time by quoting the words instead of typing seconds.
//
//   node tools/reel/words.mjs <slug> [part ...]
//       -> work/<slug>/asr/aligned_part<N>.json   { part, dur, words:[{w,s,e,src}], silences, stats }
//
//   import { clock } from '../../../tools/reel/words.mjs';
//   const K = clock('work/<slug>/asr/aligned_part1.json');
//   K.at('संवैधानिक राजतंत्र')                 // onset of the first match
//   K.at('राजा', { from: 69.5, nth: 2 })        // second match at or after 69.5 s
//   K.at('समझाइए।', { end: true })             // when that word ENDS
//   K.cut('इसके बाद पहला point')                // a scene cut just before that phrase, inside the pause
//
// TEXT   the part's HeyGen SRT, its own timings ignored (or, when the drop has
//        no SRT, work/<slug>/asr/script_part<N>.txt: the script's lines), with the video's
//        wording fixes (work/<slug>/design/wording.json: [["उन्नीस सौ नब्बे","1990"], ...])
//        so the screen shows what is WRITTEN, not how it is read.
// CLOCK  whisper.cpp word timings (work/<slug>/asr/words_part<N>.json) aligned by
//        align_words.mjs; pauses measured from the wav repair what whisper gets
//        wrong round a pause.
//
// A phrase that is not found throws, naming the words near where it looked: a
// design file that quotes a word the presenter never says must not render.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { alignWords, detectSilences } from './align_words.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const PUNCT = /[—–,.!?।…'"‘’“”:;()*★]/g;
const bare = w => w.replace(PUNCT, '').toLowerCase();

// always: how HeyGen's reading text spells what the script writes
const HOUSE_FIXES = [['barvi', '12वीं'], ['Part one', 'Part 1'], ['Part two', 'Part 2'], ['Part three', 'Part 3']];

export function captionTokens(srtPath, fixes = []) {
  let text = fs.readFileSync(srtPath, 'utf8').replace(/\r/g, '').split('\n')
    .filter(l => l.trim() && !/^\d+$/.test(l.trim()) && !l.includes('-->')).join(' ');
  for (const [from, to] of [...HOUSE_FIXES, ...fixes]) text = text.split(from).join(to);
  const toks = [];
  for (const tk of text.split(/\s+/).filter(Boolean)) {
    if (!bare(tk).replace(/-/g, '') && toks.length) toks[toks.length - 1] += ' ' + tk;   // a lone dash belongs to the word before
    else toks.push(tk);
  }
  return toks;
}

export function clock(file) {
  const A = typeof file === 'string' ? JSON.parse(fs.readFileSync(path.isAbsolute(file) ? file : path.join(ROOT, file), 'utf8')) : file;
  const W = A.words, B = W.map(w => bare(w.w));
  const find = (phrase, { from = 0, to = Infinity, nth = 1 } = {}) => {
    const p = phrase.split(/\s+/).map(bare).filter(Boolean);
    let seen = 0;
    for (let i = 0; i + p.length <= W.length; i++) {
      if (W[i].s < from - 0.02 || W[i].s >= to) continue;
      if (p.every((x, k) => B[i + k] === x) && ++seen === nth) return i;
    }
    const near = W.filter(w => w.s >= from - 0.02 && w.s < Math.min(to, from + 12)).map(w => w.w).join(' ');
    throw new Error(`part ${A.part}: "${phrase}"${nth > 1 ? ` (#${nth})` : ''} is not said in ${from}-${to === Infinity ? 'end' : to}. Heard there: ${near.slice(0, 300)}`);
  };
  const at = (phrase, o = {}) => {
    const i = find(phrase, o), n = phrase.split(/\s+/).filter(x => bare(x)).length;
    return +(o.end ? W[i + n - 1].e : W[i].s).toFixed(3);
  };
  // a cut sits in the pause before the phrase; with no pause, a frame ahead of it
  const cut = (phrase, o = {}) => {
    const i = find(phrase, o);
    if (i === 0) return 0;
    const gap = Math.max(0, W[i].s - W[i - 1].e);
    return +(W[i].s - Math.max(0.03, Math.min(0.12, gap / 2))).toFixed(3);
  };
  return { part: A.part, dur: A.dur, words: W, silences: A.silences, at, cut, find };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [slug, ...parts] = process.argv.slice(2);
  if (!slug) { console.error('usage: words.mjs <slug> [part ...]'); process.exit(2); }
  const work = path.join(ROOT, 'work', slug);
  const inputs = JSON.parse(fs.readFileSync(path.join(work, 'inputs.json'), 'utf8'));
  const wording = path.join(work, 'design/wording.json');
  const fixes = fs.existsSync(wording) ? JSON.parse(fs.readFileSync(wording, 'utf8')) : [];
  for (const P of inputs.parts) {
    if (parts.length && !parts.includes(String(P.part))) continue;
    // a drop with no SRT: the script's own text for the part, one file of plain lines
    const text = P.captions ? path.join(ROOT, P.captions.path) : path.join(work, `asr/script_part${P.part}.txt`);
    if (!fs.existsSync(text)) throw new Error(`part ${P.part}: no SRT in the drop and no ${path.relative(ROOT, text)}`);
    const toks = captionTokens(text, fixes);
    const whisper = JSON.parse(fs.readFileSync(path.join(work, `asr/words_part${P.part}.json`), 'utf8'));
    const wav = path.join(work, `asr/part${P.part}.wav`);
    const silences = fs.existsSync(wav) ? detectSilences(wav) : [];
    const { words, stats } = alignWords(toks, whisper, { duration: P.clip.duration, silences });
    const out = path.join(work, `asr/aligned_part${P.part}.json`);
    fs.writeFileSync(out, JSON.stringify({ part: P.part, dur: P.clip.duration,
      words: words.map(w => ({ w: w.w, s: +w.s.toFixed(3), e: +w.e.toFixed(3), src: w.src })), silences, stats }, null, 0));
    const weak = words.filter(w => w.src !== 'whisper').length;
    console.log(`part ${P.part}: ${words.length} words, ${weak} not matched one-to-one, ${silences.length} pauses -> ${path.relative(ROOT, out)}`);
    console.log('  ', JSON.stringify(stats));
  }
}
