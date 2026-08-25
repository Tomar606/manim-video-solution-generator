#!/usr/bin/env node
/* Emits Veo/Flow prompts for the BACKGROUND LAYER ONLY, straight from
   the same segments.json. Veo never sees a single word of script,
   so it can never misspell one.
   node bg-prompts.mjs > out/veo-background-prompts.md                */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const specs = JSON.parse(fs.readFileSync(path.join(ROOT, 'spec/segments.json'), 'utf8'));

const NEGATIVE = `any text, any letters, any words, any numbers, any mathematical symbols, any labels, any captions, any subtitles, any watermark, any logo, any UI, any signage, any handwriting, any diagram, any scientific object, any chart, any human figure. The frame must contain zero readable characters of any language, at any size, at any moment.`;

console.log(`# Veo background prompts — ${specs.length} × 10 s\n`);
console.log(`**Tool setting:** 1080×1920.  \n**Rule:** these clips carry motion and light only. Every word, label, equation and diagram is rendered separately by \`render.mjs\` and composited on top. If a generated clip contains any character of text, discard it and regenerate — do not "fix it in the edit".\n`);

for (const s of specs) {
  console.log(`\n## Segment ${s.seg_id} — ${s.type} — ${s.duration}s\n`);
  console.log('```');
  console.log(`A ${s.duration}-second vertical 9:16 abstract background plate.

SUBJECT: ${s.veo_background}

MOTION: one single continuous slow motion for the whole clip. No cuts, no
speed change, no reversal, no loop point. Motion must read the same at
second 1 and second 9.

FRAME: the composition stays uniform and uncluttered across the whole
frame. No focal object anywhere. Nothing enters or exits.

LOOK: cinematic, soft volumetric light, gentle film grain, deep shadows,
no bokeh balls, no floating particles, no lens flare.

NEGATIVE: ${NEGATIVE}`);
  console.log('```');
}

console.log(`\n---\n\n## Composite order in the editor\n
1. \`seg-N.mov\` background plate (from Veo)  — bottom
2. \`out/seg-N.mov\` truth layer, ProRes 4444 alpha — middle
3. HeyGen avatar, green-screen keyed, anchored to the lower 960 px — top

The truth layer is already 1080×1920 with everything below y=960
transparent, so it drops on with zero alignment work.`);
