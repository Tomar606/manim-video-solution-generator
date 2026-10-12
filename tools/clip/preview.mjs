/* preview.mjs — scrub a part in a real browser before rendering it.
 *
 *   node tools/clip/preview.mjs <slug> --part 1     -> http://localhost:5178/renderer/index.html?spec=…
 *
 * Same engine, same video.css, same spec the render will use.
 */
import { parseArgs, videoDir, loadVideo, specOf, serve } from './lib.mjs';

const a = parseArgs();
const dir = videoDir(a._[0]);
const cfg = loadVideo(dir);
const { rel } = specOf(dir, a);
const { port } = await serve(cfg, Number(a.port || 5178));
console.log(`preview:  http://localhost:${port}/renderer/index.html?spec=${encodeURIComponent(rel)}`);
console.log('scrub through each segment here BEFORE you render.');
