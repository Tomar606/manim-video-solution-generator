#!/usr/bin/env node
/* One frame, instantly. node snap.mjs <seg_id> <t> [out.png]
   Use this while tuning timing — 3 seconds instead of a 90-second render. */
import { chromium } from 'playwright';
import fs from 'node:fs'; import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { serve } from './server.mjs';
const ROOT = path.dirname(fileURLToPath(import.meta.url));
const specs = JSON.parse(fs.readFileSync(path.join(ROOT,'spec/segments.json'),'utf8'));
const id = Number(process.argv[2]), t = Number(process.argv[3] ?? 5);
const i = specs.findIndex(s => s.seg_id === id);
if (i < 0) { console.error('no such seg_id'); process.exit(1); }
const { server, port } = await serve(ROOT);
const b = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
const p = await b.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
p.on('pageerror', e => console.error('SPEC ERROR:', e.message));
await p.goto(`http://127.0.0.1:${port}/renderer/index.html?seg=${i}&headless=1`);
await p.waitForFunction('window.READY === true'); await p.evaluate(() => document.fonts.ready);
await p.evaluate(t => window.RENDER.setTime(t), t);
const out = process.argv[4] ?? path.join(ROOT,'out',`snap-${id}-${t}.png`);
await p.screenshot({ path: out, omitBackground: true });
await b.close(); server.close(); console.log(out);
