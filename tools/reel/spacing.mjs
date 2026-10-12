// arts/DESIGN_RULES.md section 2 ("let the design breathe"), measured instead of eyeballed.
//
//   DUMP_HTML=/tmp/page.html node work/<slug>/design/part<N>.mjs     (a kit whose cli honours DUMP_HTML)
//   node tools/reel/spacing.mjs <slug> <part> /tmp/page.html
//
// At 55 % of every scene and just before its end, every visible timeline element (.it, and each
// svg.sv drawing as the union of its visible parts) is boxed; it prints pairs closer than 40 px,
// overlaps, content above the top line (190 under an eyebrow, else 120), left of the 64 px margin,
// and below the presenter's line for that scene (look.json place: you 900, explain 1170, small 1440).
// Overlaps that are meant (a tick on its card, an arrow over steps) are listed too: read, don't obey.
// Written for GEO-C3-SA-01 after the user asked for breathing space (2026-10-09).
import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module'; import { fileURLToPath } from 'node:url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const require = createRequire(path.join(ROOT, 'tools/clip/package.json'));
const { chromium } = require('playwright');
const [SLUG, PART, PAGE] = process.argv.slice(2);
if (!PAGE) { console.error('usage: spacing.mjs <slug> <part> <page.html>'); process.exit(2); }
const html = fs.readFileSync(PAGE, 'utf8');
const spec = JSON.parse(fs.readFileSync(path.join(ROOT, `work/${SLUG}/scenes_part${PART}.json`), 'utf8'));
const LIMIT = { you: 900, explain: 1170, small: 1440, hidden: 1680 };
const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await pg.setContent(html); await pg.evaluate(() => window.READY);
for (const s of spec.scenes) {
  for (const t of [s.t0 + (s.t1 - s.t0) * .55, s.t1 - .05]) {
    const boxes = await pg.evaluate(t => {
      window.render(t, 'overlay');
      const vis = e => { const cs = getComputedStyle(e); return cs.visibility !== 'hidden' && +cs.opacity > .5 && cs.display !== 'none'; };
      const out = [];
      // html items not inside another item
      for (const e of document.querySelectorAll('#L_overlay .it')) {
        if (!vis(e) || e.parentElement.closest('.it')) continue;
        const r = e.getBoundingClientRect(); if (r.width < 2) continue;
        out.push({ k: (e.className.split(' ')[1] || e.id) + ':' + (e.innerText || '').trim().slice(0, 14).replace(/\n/g, ' '), x0: r.left, y0: r.top, x1: r.right, y1: r.bottom });
      }
      // each svg drawing as the union of its visible parts
      for (const sv of document.querySelectorAll('#L_overlay svg.sv')) {
        if (sv.id === 'sw' || sv.id === 'pf') continue;
        let u = null;
        for (const e of sv.querySelectorAll('.svi')) {
          if (!vis(e)) continue; const r = e.getBoundingClientRect(); if (r.width < 1 && r.height < 1) continue;
          u = u ? { x0: Math.min(u.x0, r.left), y0: Math.min(u.y0, r.top), x1: Math.max(u.x1, r.right), y1: Math.max(u.y1, r.bottom) } : { x0: r.left, y0: r.top, x1: r.right, y1: r.bottom };
        }
        if (u) out.push({ k: 'svg:' + ((sv.textContent || '').trim().slice(0, 10) || 'drawing'), ...u });
      }
      return out;
    }, t);
    const pin = s.shots.find(x => x.pin && t >= x.t0 && t < x.t1);
    if (pin) boxes.push({ k: 'PINNED CLIP', x0: pin.pin[0], y0: pin.pin[1], x1: pin.pin[0] + pin.pin[2], y1: pin.pin[1] + pin.pin[3] });
    const issues = [];
    const eb = boxes.some(q => q.k.startsWith('eb'));
    for (const q of boxes) {
      if (q.k.startsWith('eb')) continue;
      const top = eb ? 190 : 120;
      if (q.y0 < top - 1) issues.push(`top ${Math.round(q.y0)} < ${top}: ${q.k}`);
      if (q.y1 > LIMIT[s.presenter] + 1) issues.push(`bottom ${Math.round(q.y1)} > ${LIMIT[s.presenter]} (${s.presenter}): ${q.k}`);
      if (q.x0 < 63 && q.x1 > 70) issues.push(`left ${Math.round(q.x0)} < 64: ${q.k}`);
    }
    for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], c = boxes[j];
      const gx = Math.max(c.x0 - a.x1, a.x0 - c.x1), gy = Math.max(c.y0 - a.y1, a.y0 - c.y1), gap = Math.max(gx, gy);
      if (gap < 40) issues.push(`${gap < 0 ? 'OVERLAP' : 'gap ' + Math.round(gap)}  ${a.k}  <->  ${c.k}`);
    }
    if (issues.length) console.log(`${s.id} @${t.toFixed(2)} (${s.presenter})\n  ` + [...new Set(issues)].join('\n  '));
  }
}
await b.close();
