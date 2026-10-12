// Put a clock on caption words: align the words a caption SHOWS to the words
// whisper.cpp HEARD, and return an onset and an end for every caption word.
//
//   import { alignWords, detectSilences } from 'tools/reel/align_words.mjs';
//   const sil = detectSilences('work/<slug>/asr/part1.wav');          // optional
//   const { words, stats } = alignWords(['MP', 'Board', 'कक्षा', ...], whisperWords,
//                                       { duration: 141.6, silences: sil });
//   words[i] = { w, s, e, src, heard, sim, whisper_s }
//
// Whisper is used ONLY for timing — its spelling is wrong often, it drops words,
// it splits one word in two ("भू" "आकरती") and glues two into one. So:
//
//   * matching is a global sequence alignment (Needleman-Wunsch, cheap gaps) on
//     NORMALISED text: matras, nasal marks, aspiration and श/स are folded
//     together, and a Latin or numeric caption word is compared in the forms it
//     is SAID in ("Exam" ~ "एक्जाम", "12वीं" ~ "12").
//   * one caption word may take two whisper tokens (src 'whisper-joined') and
//     two caption words may share one token (src 'whisper-split').
//   * a caption word nothing matched is placed between its matched neighbours
//     in proportion to its length (src 'interpolated').
//   * onsets come out strictly increasing.
//
// Silences (measured from the audio, optional) repair the two things whisper's
// contiguous timestamps get wrong around a pause: a word stamped INSIDE the
// pause really starts when the sound comes back, and a word before a pause ends
// when the sound stops, not when the next word starts.
//
// whisper words: [{ w, s, e }] in seconds ({ w, t } is accepted: end = next t).
import { spawnSync } from 'node:child_process';

// How a non-Devanagari caption token is SAID. Extend per video with opts.said.
export const SAID = {
  mp: ['एमपी', 'एम्पी'], board: ['बोर्ड'], exam: ['एग्जाम', 'एक्जाम', 'इग्जाम'], exams: ['एग्जाम्स'],
  question: ['क्वेश्चन', 'क्वेस्चन'], answer: ['आंसर', 'आन्सर'], line: ['लाइन'], lines: ['लाइन्स'],
  part: ['पार्ट'], important: ['इम्पोर्टेंट', 'इंपॉर्टेंट'], point: ['पॉइंट'], points: ['पॉइंट्स'],
  main: ['मेन'], topic: ['टॉपिक'], marks: ['मार्क्स'], class: ['क्लास'], note: ['नोट'], ncert: ['एनसीईआरटी'],
  '1': ['एक', 'वन', 'one'], '2': ['दो', 'टू', 'two'], '3': ['तीन', 'थ्री', 'three'], '4': ['चार', 'फोर', 'four'],
  '5': ['पाँच', 'फाइव', 'five'], '10वीं': ['दसवीं', '10'], '12वीं': ['बारवीं', 'बारहवीं', '12'],
};

const PUNCT = /[—–,.!?।…'"‘’“”:;()]/g;
const FOLD = { 'ी': 'ि', 'ू': 'ु', 'ै': 'े', 'ौ': 'ो', 'ॉ': 'ो', 'ई': 'इ', 'ऊ': 'उ', 'ऐ': 'ए', 'औ': 'ओ', 'आ': 'अ',
  'ख': 'क', 'घ': 'ग', 'छ': 'च', 'झ': 'ज', 'ठ': 'ट', 'ढ': 'ड', 'थ': 'त', 'ध': 'द', 'फ': 'प', 'भ': 'ब',
  'श': 'स', 'ष': 'स', 'ण': 'न', 'व': 'ब', 'ऋ': 'र', 'ृ': 'र', '-': '' };
// "येवं" for "एवं", "गयी" for "गई", "लिये" for "लिए": whisper's य-glide spellings
const fold = s => [...s.normalize('NFD').replace(/[़ँंः्]/g, '').replace(/ये/g, 'ए').replace(/य[िी]/g, 'इ')].map(c => FOLD[c] ?? c).join('');
const bare = s => s.toLowerCase().replace(PUNCT, '').trim();

/** Normalised form of a word as it is written. */
export const norm = s => fold(bare(s));
/** Every normalised form a caption word may be heard as. */
function forms(word, said) {
  const b = bare(word);
  return [...new Set([fold(b), ...(said[b] || []).map(a => fold(a.toLowerCase()))])].filter(Boolean);
}
/** Letters that take time to say — what an unmatched word's share is measured in. */
export const letters = w => [...w.replace(PUNCT, '').replace(/[-़्]/g, '')].length || 1;

function lev(a, b) {
  a = [...a]; b = [...b];
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++)
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    prev = cur;
  }
  return prev[b.length];
}
// 1 = same word. One string being the other's prefix ("साथ-साथ" heard as "साथ")
// counts as a fair match: the onset is still the right one.
function simForms(fs, y) {
  let best = 0;
  if (!y) return 0;
  for (const x of fs) {
    const lx = [...x].length, ly = [...y].length;
    let v = 1 - lev(x, y) / Math.max(lx, ly);
    if (Math.min(lx, ly) >= 2 && (y.startsWith(x) || x.startsWith(y))) v = Math.max(v, 0.7);
    if (v > best) best = v;
  }
  return best;
}

/** Silent stretches of an audio file: [[start, end], ...] in seconds. */
export function detectSilences(audio, { noise = -35, min = 0.15 } = {}) {
  const r = spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-i', audio, '-af',
    `silencedetect=noise=${noise}dB:d=${min}`, '-f', 'null', '-'], { encoding: 'utf8', maxBuffer: 1 << 26 });
  if (r.status !== 0) throw new Error('silencedetect failed on ' + audio + '\n' + r.stderr.slice(-400));
  const out = []; let a = null;
  for (const m of r.stderr.matchAll(/silence_(start|end): (-?[\d.]+)/g)) {
    if (m[1] === 'start') a = Math.max(0, +m[2]);
    else if (a !== null) { out.push([a, +m[2]]); a = null; }
  }
  return out;
}

/** Drop whisper's hallucinated bursts and stutters; returns clean [{w,s,e}]. */
export function cleanWhisper(raw) {
  let W = raw.map((x, i) => ({ w: x.w, s: x.s ?? x.t, e: x.e ?? raw[i + 1]?.s ?? raw[i + 1]?.t ?? (x.s ?? x.t) + 0.3 }))
    .filter(x => x.w && norm(x.w));
  // a burst of tokens stamped with one identical time is a hallucinated repeat
  const cnt = {}; for (const x of W) cnt[x.s] = (cnt[x.s] || 0) + 1;
  W = W.filter(x => cnt[x.s] < 3);
  // a word that repeats the next one within 0.3 s: keep the later, the real take
  W = W.filter((x, i) => !(W[i + 1] && norm(W[i + 1].w) === norm(x.w) && W[i + 1].s - x.s < 0.3));
  return W;
}

/** Move whisper boundaries that sit in measured silence. Returns copies with s0/e0 = as heard. */
export function applySilences(W, silences = []) {
  const long = silences.filter(([a, b]) => b - a >= 0.3);
  return W.map(x => {
    const y = { ...x, s0: x.s, e0: x.e };
    // stamped well inside a pause -> starts when the sound comes back
    const inside = long.find(([a, b]) => y.s >= a + 0.08 && y.s < b - 0.08);
    if (inside) { y.s = +inside[1].toFixed(3); y.moved = true; if (y.e < y.s + 0.1) y.e = +(y.s + 0.1).toFixed(3); }
    // a pause begins during the word -> it ends there
    const cut = silences.find(([a]) => a > y.s + 0.05 && a < y.e);
    if (cut) y.e = +cut[0].toFixed(3);
    // stamped a hair after the sound stopped: it is the word BEFORE the pause, just late
    else if (silences.some(([a, b]) => y.s >= a && y.s < a + 0.08 && b > y.s + 0.15)) y.e = +Math.min(y.e, y.s + 0.15).toFixed(3);
    return y;
  });
}

/**
 * @param {Array<string|{text:string}>} captionWords  words as shown (punctuation may be attached)
 * @param {Array<{w:string,s:number,e:number}>} whisperWords
 * @param {{duration?:number, silences?:number[][], said?:object, minSim?:number, minStep?:number}} opts
 * @returns {{words: Array<{w,s,e,src,heard,sim,whisper_s}>, stats: object}}
 */
export function alignWords(captionWords, whisperWords, opts = {}) {
  const { duration = Infinity, silences = [], minSim = 0.45, minStep = 0.06 } = opts;
  const said = { ...SAID, ...(opts.said || {}) };
  const C = captionWords.map(c => { const text = typeof c === 'string' ? c : c.text; return { w: text, f: forms(text, said), n: letters(text) }; });
  const W = applySilences(cleanWhisper(whisperWords), silences).map(x => ({ ...x, n: norm(x.w) }));
  const N = C.length, M = W.length;

  // ---- global alignment -------------------------------------------------------
  // moves: 1 caption skipped | 2 whisper skipped | 3 one-to-one |
  //        4 one caption word = two whisper tokens | 5 two caption words = one token
  const SKIP_C = -0.15, SKIP_W = -0.05, NEG = -1e9;
  const s11 = (i, j) => { const v = simForms(C[i].f, W[j].n); return v >= minSim ? v : NEG; };
  const s12 = (i, j) => {                       // "भू-आकृति" heard as "भू" "आकरती"
    if (W[j + 1].s - W[j].e > 0.35) return NEG;
    const v = simForms(C[i].f, W[j].n + W[j + 1].n);
    return v >= 0.6 && v > Math.max(simForms(C[i].f, W[j].n), simForms(C[i].f, W[j + 1].n)) ? v + 0.1 : NEG;
  };
  const s21 = (i, j) => {                       // "ईसा पूर्व" heard as "इसापूर्व"
    const joined = [norm(C[i].w) + norm(C[i + 1].w)];
    const v = simForms(joined, W[j].n);
    return v >= 0.75 && v > Math.max(simForms(C[i].f, W[j].n), simForms(C[i + 1].f, W[j].n)) ? 2 * v - 0.1 : NEG;
  };
  const D = Array.from({ length: N + 1 }, () => new Float64Array(M + 1));
  const B = Array.from({ length: N + 1 }, () => new Uint8Array(M + 1));
  for (let i = 1; i <= N; i++) { D[i][0] = D[i - 1][0] + SKIP_C; B[i][0] = 1; }
  for (let j = 1; j <= M; j++) { D[0][j] = D[0][j - 1] + SKIP_W; B[0][j] = 2; }
  for (let i = 1; i <= N; i++) for (let j = 1; j <= M; j++) {
    let best = D[i - 1][j] + SKIP_C, b = 1;
    let v = D[i][j - 1] + SKIP_W; if (v > best) { best = v; b = 2; }
    v = D[i - 1][j - 1] + s11(i - 1, j - 1); if (v > best) { best = v; b = 3; }
    if (j >= 2) { v = D[i - 1][j - 2] + s12(i - 1, j - 2); if (v > best) { best = v; b = 4; } }
    if (i >= 2) { v = D[i - 2][j - 1] + s21(i - 2, j - 1); if (v > best) { best = v; b = 5; } }
    D[i][j] = best; B[i][j] = b;
  }
  const out = C.map(c => ({ w: c.w, s: undefined, e: undefined, src: 'interpolated', heard: null, sim: 0, whisper_s: null }));
  const set = (i, o) => Object.assign(out[i], o);
  for (let i = N, j = M; i > 0 || j > 0;) {
    const b = B[i][j];
    if (b === 3) {
      const x = W[j - 1];
      set(i - 1, { s: x.s, e: x.e, src: x.moved ? 'whisper-after-pause' : 'whisper', heard: x.w, sim: +simForms(C[i - 1].f, x.n).toFixed(2), whisper_s: x.s0 });
      i--; j--;
    } else if (b === 4) {
      const x = W[j - 2], y = W[j - 1];
      set(i - 1, { s: x.s, e: y.e, src: 'whisper-joined', heard: x.w + ' ' + y.w, sim: +simForms(C[i - 1].f, x.n + y.n).toFixed(2), whisper_s: x.s0 });
      i--; j -= 2;
    } else if (b === 5) {
      const x = W[j - 1], a = C[i - 2].n, c = C[i - 1].n, mid = +(x.s + (x.e - x.s) * a / (a + c)).toFixed(3);
      const v = +simForms([norm(C[i - 2].w) + norm(C[i - 1].w)], x.n).toFixed(2);
      set(i - 2, { s: x.s, e: mid, src: 'whisper-split', heard: x.w, sim: v, whisper_s: x.s0 });
      set(i - 1, { s: mid, e: x.e, src: 'whisper-split', heard: x.w, sim: v, whisper_s: x.s0 });
      i -= 2; j--;
    } else if (b === 1) i--; else j--;
  }

  // ---- unmatched words: between their matched neighbours, by length --------------
  // The run's clock runs from the left neighbour's onset to the right neighbour's
  // onset — or to where the sound stops, if a pause sits just before the right one.
  const soundStopsBefore = (t, after) => {
    const p = silences.find(([a, b]) => b > t - 0.12 && a < t && a > after + 0.1);
    return p ? p[0] : t;
  };
  for (let k = 0; k < N;) {
    if (out[k].s !== undefined) { k++; continue; }
    let r = k; while (r < N && out[r].s === undefined) r++;
    const L = k > 0 ? out[k - 1] : null, R = r < N ? out[r] : null;
    const run = C.slice(k, r).reduce((a, c) => a + c.n, 0), lead = L ? C[k - 1].n : 0;
    let ta, tb;
    if (L && R) { ta = L.s; tb = soundStopsBefore(R.s, ta); }
    else if (L) { ta = L.s; tb = Math.min(duration, Math.max(L.e, ta + (lead + run) * 0.07)); }
    else if (R) { tb = R.s; ta = Math.max(0, Math.min(W[0]?.s ?? tb, tb - run * 0.07)); }
    else { ta = 0; tb = Math.min(duration, run * 0.07); }
    let acc = lead;
    for (let q = k; q < r; q++) {
      out[q].s = +(ta + (tb - ta) * acc / (lead + run)).toFixed(3);
      acc += C[q].n;
      out[q].e = +(ta + (tb - ta) * acc / (lead + run)).toFixed(3);
    }
    if (L) L.e = Math.min(L.e, out[k].s);
    k = r;
  }

  // ---- strictly increasing onsets; an end never passes the next onset ----------------
  let pushed = 0;
  for (let i = 1; i < N; i++) if (out[i].s < out[i - 1].s + minStep) { out[i].s = +(out[i - 1].s + minStep).toFixed(3); out[i].pushed = true; pushed++; }
  for (let i = 0; i < N; i++) {
    const next = i + 1 < N ? out[i + 1].s : duration;
    out[i].e = +Math.max(out[i].s + 0.05, Math.min(out[i].e, next, duration)).toFixed(3);
    out[i].s = +out[i].s.toFixed(3);
  }
  const count = s => out.filter(o => o.src === s).length;
  return {
    words: out,
    stats: {
      caption_words: N, whisper_words: M, matched: N - count('interpolated'), interpolated: count('interpolated'),
      joined: count('whisper-joined'), split: count('whisper-split'), after_pause: count('whisper-after-pause'),
      weak: out.filter(o => o.src !== 'interpolated' && o.sim < 0.6).length, pushed,
    },
  };
}
