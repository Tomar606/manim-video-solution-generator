/* qa.mjs — automated visual QA. Run this BEFORE showing anything to the user.
 *
 *   node qa.mjs            all segments
 *   node qa.mjs 3,5        just those
 *
 * validate.py checks the spec on paper. This checks what actually lands on the
 * pixels, by walking every segment frame-by-frame in the real browser and
 * measuring the real DOM boxes. Every check here exists because a real reel
 * shipped with that defect.
 *
 * FAILS (must fix):
 *   ORPHAN      an id is scheduled but never becomes visible
 *               (classic cause: its only action is `draw`)
 *   OVERFLOW    a label is wider/taller than the shape it sits in
 *   OVERLAP     two labels collide
 *   OUTSIDE     a label leaves the stage, or anything crosses y=960
 *   EMPTY_BOX   a container shape sits empty for over 1.5 s while other
 *               labels are already up — looks broken on screen
 *   LONE        the diagram shows a single stray element for over 2 s
 *   NO_DIAGRAM  the diagram zone is empty too long. A deliberate late entry is
 *               fine — an intro line often speaks before anything is drawn — so
 *               the lead-in is allowed up to 5 s. Once the diagram HAS appeared,
 *               a hole of more than 2 s is a bug.
 *   BOTH_SIDES  elements from two different topics are on screen together.
 *               Ids beginning g_/cmp_g/gal_ are side A, e_/cmp_e/ele_ are side B.
 *               Only whatever is being spoken about right now may be visible.
 *               Set "allow_both": true on the segment if the script really is
 *               comparing them in the same breath.
 *   COLON       a phrase uses a colon as a shortcut instead of natural wording
 *
 * WARNINGS: worth a look, not automatically wrong.
 */
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { serve } from './server.mjs';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const STEP = 0.2;                      // sample every 200 ms
const HALF = 960;                      // avatar line: nothing may cross it

let specs = JSON.parse(fs.readFileSync(path.join(ROOT, 'spec/segments.json'), 'utf8'));
const pick = process.argv[2];
if (pick) {
  const want = new Set(pick.split(',').map(Number));
  specs = specs.filter(s => want.has(s.seg_id));
}

const { server, port } = await serve(ROOT);
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto(`http://localhost:${port}/renderer/index.html?headless=1`, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.READY === true);

const fails = [], warns = [];
const F = (sid, code, msg) => fails.push(`seg ${sid}  ${code.padEnd(10)} ${msg}`);
const W = (sid, code, msg) => warns.push(`seg ${sid}  ${code.padEnd(10)} ${msg}`);

for (const seg of specs) {
  const sid = seg.seg_id;
  await page.evaluate(async s => { await window.RENDER.build(s); window.RENDER.setTime(0); }, seg);

  const frames = [];
  for (let t = 0; t <= seg.duration + 1e-6; t = +(t + STEP).toFixed(2)) {
    frames.push(await page.evaluate(time => {
      window.RENDER.setTime(time);
      const vis = el => {
        const o = parseFloat(getComputedStyle(el).opacity || '1');
        const r = el.getBoundingClientRect();
        // a horizontal rule has zero height and a vertical one zero width,
        // so require area on EITHER axis, not both
        return o > 0.15 && (r.width > 0 || r.height > 0) && getComputedStyle(el).display !== 'none';
      };
      const labels = [...document.querySelectorAll('#stage .lbl')].filter(vis).map(e => {
        const r = e.getBoundingClientRect();
        return { text: e.textContent, x: r.x, y: r.y, w: r.width, h: r.height,
                 right: r.right, bottom: r.bottom };
      });
      const svg = document.querySelector('#stage svg');
      const shapes = svg ? [...svg.querySelectorAll('[id]')].filter(vis).map(e => {
        const r = e.getBoundingClientRect();
        return { id: e.id, tag: e.tagName, x: r.x, y: r.y, w: r.width, h: r.height,
                 right: r.right, bottom: r.bottom,
                 // a "container" is a big rounded shape meant to hold a label
                 box: (e.tagName === 'rect' || e.tagName === 'g') && r.width > 140 && r.height > 50 };
      }) : [];
      const caption = [...document.querySelectorAll('#caption .phrase')]
        .filter(vis).map(e => { const r = e.getBoundingClientRect();
          return { text: e.textContent, bottom: r.bottom, right: r.right, x: r.x }; });
      return { t: time, labels, shapes, caption };
    }, t));
  }

  /* --- ORPHAN: scheduled but never visible --- */
  const scheduled = new Set([...(seg.diagram?.carry_over || []),
                             ...(seg.diagram?.timeline || []).map(a => a.id)]);
  const everSeen = new Set();
  frames.forEach(f => f.shapes.forEach(s => everSeen.add(s.id)));
  for (const id of scheduled) {
    if (everSeen.has(id)) continue;
    const acts = (seg.diagram.timeline || []).filter(a => a.id === id).map(a => a.action);
    const hint = acts.length && acts.every(a => a === 'draw')
      ? ' (only action is `draw` — pair it with fade_in)' : '';
    F(sid, 'ORPHAN', `"${id}" is scheduled but never appears${hint}`);
  }
  for (const l of (seg.labels || [])) {
    if (!frames.some(f => f.labels.some(x => x.text === l.text)))
      F(sid, 'ORPHAN', `label "${l.text}" never appears`);
  }

  /* --- wording: colons are a crutch, write it the way it is spoken --- */
  for (const p of seg.phrases)
    if (p.text.includes(':')) F(sid, 'COLON', `phrase uses a colon: "${p.text}"`);

  /* --- per-frame geometry ---
     The avatar line only binds while the avatar is THERE. A segment that
     declares its own taller stage is one the presenter fades out of, so the
     limit for it is the bottom of that stage instead of the halfway line.
     Everywhere else 960 still holds, and a segment may not claim a tall stage
     without the presenter-hide window to match -- build_dry.py writes both from
     the same plan so they cannot drift apart. */
  const floor = seg.stage ? seg.stage.top + seg.stage.h : HALF;
  let loneRun = 0, emptyRun = new Map(), noDiagRun = 0, started = false;
  for (const f of frames) {
    for (const l of f.labels) {
      if (l.bottom > floor) F(sid, 'OUTSIDE', `label "${l.text}" falls below ${floor}px at ${f.t}s`);
      if (l.x < 0 || l.right > 1080) F(sid, 'OUTSIDE', `label "${l.text}" leaves the frame at ${f.t}s`);

      // label must fit inside whatever container it sits in
      for (const s of f.shapes.filter(s => s.box)) {
        const inside = l.x + l.w / 2 > s.x && l.x + l.w / 2 < s.right &&
                       l.y + l.h / 2 > s.y && l.y + l.h / 2 < s.bottom;
        if (inside && (l.w > s.w - 16 || l.h > s.h - 8))
          F(sid, 'OVERFLOW', `label "${l.text}" (${Math.round(l.w)}px) does not fit shape "${s.id}" (${Math.round(s.w)}px) at ${f.t}s`);
      }
    }
    for (let i = 0; i < f.labels.length; i++)
      for (let j = i + 1; j < f.labels.length; j++) {
        const a = f.labels[i], b = f.labels[j];
        const ox = Math.min(a.right, b.right) - Math.max(a.x, b.x);
        const oy = Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y);
        if (ox > 6 && oy > 6)
          F(sid, 'OVERLAP', `labels "${a.text}" and "${b.text}" collide at ${f.t}s`);
      }
    for (const c of f.caption)
      if (c.bottom > 380) W(sid, 'CAPTION', `caption "${c.text.slice(0,28)}" reaches the diagram zone at ${f.t}s`);

    // container visible but still empty, while other labels are already up
    for (const s of f.shapes.filter(s => s.box && s.tag === 'rect')) {
      const filled = f.labels.some(l => l.x + l.w / 2 > s.x && l.x + l.w / 2 < s.right &&
                                        l.y + l.h / 2 > s.y && l.y + l.h / 2 < s.bottom);
      const k = s.id + '|' + Math.round(s.x);
      const run = filled || f.labels.length === 0 ? 0 : (emptyRun.get(k) || 0) + STEP;
      emptyRun.set(k, run);
      if (Math.abs(run - 1.6) < STEP / 2)
        F(sid, 'EMPTY_BOX', `shape "${s.id}" sits empty >1.5s while other labels are up (from ${(f.t - run).toFixed(1)}s)`);
    }

    // only one topic may be on screen at a time
    if (!seg.allow_both) {
      const side = id => /^(cmp_g|gal_|g_)/.test(id) ? 'A'
                       : /^(cmp_e|ele_|e_)/.test(id) ? 'B' : null;
      const a = f.shapes.filter(s => side(s.id) === 'A').map(s => s.id);
      const b = f.shapes.filter(s => side(s.id) === 'B').map(s => s.id);
      if (a.length && b.length)
        F(sid, 'BOTH_SIDES', `"${a[0]}" and "${b[0]}" are both on screen at ${f.t}s`);
    }

    loneRun = f.shapes.length === 1 && f.labels.length === 0 ? loneRun + STEP : 0;
    if (Math.abs(loneRun - 2.2) < STEP / 2)
      F(sid, 'LONE', `only "${f.shapes[0].id}" on screen for >2s (from ${(f.t - loneRun).toFixed(1)}s)`);

    if (seg.diagram) {
      if (f.shapes.length) { noDiagRun = 0; started = true; }
      else noDiagRun += STEP;
      // lead-in may be long on purpose; a hole after the diagram started may not
      const limit = started ? 2.2 : 5.0;
      if (Math.abs(noDiagRun - limit) < STEP / 2)
        F(sid, 'NO_DIAGRAM', started
          ? `diagram vanishes mid-segment for >2s (from ${(f.t - noDiagRun).toFixed(1)}s)`
          : `nothing drawn for the first ${limit}s`);
    }
  }
}

await browser.close();
server.close();

const uniq = a => [...new Set(a)];
const f = uniq(fails), w = uniq(warns);
console.log(`\nQA — ${specs.length} segment(s), sampled every ${STEP}s`);
console.log(`\nFAILS (${f.length}):`);
console.log(f.length ? f.map(x => '  X ' + x).join('\n') : '  none');
console.log(`\nWARNINGS (${w.length}):`);
console.log(w.length ? w.map(x => '  ! ' + x).join('\n') : '  none');
process.exitCode = f.length ? 1 : 0;
