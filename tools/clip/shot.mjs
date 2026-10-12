/* shot.mjs — snapshot any local page or SVG.
 *
 *   node tools/clip/shot.mjs <file.svg|file.html> <out.png> [--w 1080 --h 470]
 *
 * For checking a diagram on its own while it is being drawn. An SVG is laid on
 * the engine's dark stage colour so thin strokes read the way they will render.
 */
import path from 'node:path';
import fs from 'node:fs';
import { launch, newPage, die } from './lib.mjs';

const args = process.argv.slice(2);
const opt = k => { const i = args.indexOf(`--${k}`); return i >= 0 ? Number(args[i + 1]) : null; };
const [file, out] = args.filter((x, i) => !x.startsWith('--') && !args[i - 1]?.startsWith('--'));
if (!file || !out) die('usage: node tools/clip/shot.mjs <file> <out.png> [--w W --h H]');
const isSvg = file.toLowerCase().endsWith('.svg');
const w = opt('w') ?? 1080, h = opt('h') ?? (isSvg ? 470 : 1920);
const b = await launch();
const p = await newPage(b, w, h);
if (isSvg) {
  const svg = fs.readFileSync(file, 'utf8');
  await p.setContent(`<!doctype html><style>html,body{margin:0;background:#0B1A2E}
    svg{display:block;width:${w}px;height:${h}px}</style>${svg}`);
} else {
  await p.goto('file://' + path.resolve(file));
}
await p.waitForTimeout(300);
await p.screenshot({ path: out });
await b.close();
console.log('->', out);
