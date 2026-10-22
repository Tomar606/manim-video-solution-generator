/**
 * Fetch the geographic datasets and TRIM them before they are stored.
 *
 *   node map_engine/data/fetch.mjs
 *
 * WHY TRIM. The Natural Earth admin-1 file is 40 MB of every province on
 * Earth; this engine needs India's 36. The raw download is written to a temp
 * path, filtered, and deleted — the machine this runs on has had a build die
 * of a full disk before, and a data layer that quietly grows to a gigabyte is
 * the same failure waiting to happen.
 *
 * EVERY DATASET RECORDS ITS LICENCE. Natural Earth is public domain, which is
 * why it is the default for a commercial product. GADM — the obvious
 * alternative for Indian districts — is licensed for academic use only and
 * must NOT be used here. See data/LICENSES.md.
 */
import { writeFile, mkdir, readFile } from 'fs/promises';
import { existsSync } from 'fs';
import { join } from 'path';

const ROOT = new URL('.', import.meta.url).pathname;
const RAW = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson';

// Around India, so neighbouring landmasses are drawn rather than ending at a
// hard rectangle. Generous: the camera zooms out to the whole country.
const BBOX = [60, 5, 100, 40];          // west, south, east, north

const JOBS = [
  // INDIA'S POINT OF VIEW, NOT THE DEFAULT.
  //
  // Natural Earth's default edition draws India along the de-facto Line of
  // Control: the polygon stops at 35.50 N, so Gilgit-Baltistan and Aksai Chin
  // are outside India. Publishing that on an Indian edtech platform shows the
  // country's territory as not its own, which is a legal and reputational
  // problem, not a cartographic nicety.
  //
  // Natural Earth ships per-country worldviews for exactly this. The `_ind`
  // edition reaches 37.05 N — the full claim — and reduces the neighbouring
  // polygons to match, so the map is internally consistent rather than having
  // two countries claim the same ground. It is the same public-domain licence.
  //
  // There is no `_ind` edition of admin-1, so state BORDERS do not subdivide
  // the north. That is acceptable and the land is still drawn as India: the
  // offence is depicting Indian territory as foreign, not leaving it
  // undivided. `countries` is what fills the land, so nothing reads as missing.
  { file: 'ne_10m_admin_0_countries_ind.geojson', out: 'countries.geojson',
    keep: f => bboxHits(f), slim: ['NAME', 'NAME_HI', 'ADM0_A3', 'CONTINENT'] },
  { file: 'ne_10m_admin_1_states_provinces.geojson', out: 'india_states.geojson',
    keep: f => f.properties.admin === 'India',
    slim: ['name', 'name_hi', 'adm1_code', 'type_en', 'admin'] },
  { file: 'ne_50m_rivers_lake_centerlines.geojson', out: 'rivers.geojson',
    keep: f => bboxHits(f), slim: ['name', 'name_hi'] },
  { file: 'ne_50m_lakes.geojson', out: 'lakes.geojson',
    keep: f => bboxHits(f), slim: ['name'] },
];

function coordsOf(g, out = []) {
  if (!g) return out;
  if (g.type === 'GeometryCollection') { g.geometries.forEach(x => coordsOf(x, out)); return out; }
  const walk = c => (typeof c[0] === 'number') ? out.push(c) : c.forEach(walk);
  walk(g.coordinates);
  return out;
}

function bboxHits(f) {
  const [w, s, e, n] = BBOX;
  return coordsOf(f.geometry).some(([x, y]) => x >= w && x <= e && y >= s && y <= n);
}

function slimProps(p, keep) {
  const o = {};
  for (const k of keep) if (p[k] !== undefined && p[k] !== null) o[k] = p[k];
  return o;
}

await mkdir(join(ROOT, 'derived'), { recursive: true });
const manifest = [];

for (const job of JOBS) {
  const dest = join(ROOT, 'derived', job.out);
  if (existsSync(dest)) {
    console.log(`  ${job.out} — cached`);
    manifest.push({ out: job.out, source: `${RAW}/${job.file}`, cached: true });
    continue;
  }
  process.stdout.write(`  ${job.file} … `);
  const r = await fetch(`${RAW}/${job.file}`);
  if (!r.ok) throw new Error(`${job.file}: HTTP ${r.status}`);
  const fc = JSON.parse(await r.text());
  const features = fc.features.filter(job.keep)
    .map(f => ({ type: 'Feature', properties: slimProps(f.properties, job.slim),
                 geometry: f.geometry }));
  await writeFile(dest, JSON.stringify({ type: 'FeatureCollection', features }));
  const kb = Math.round((await readFile(dest)).length / 1024);
  console.log(`${fc.features.length} -> ${features.length} features, ${kb} KB`);
  manifest.push({ out: job.out, source: `${RAW}/${job.file}`,
                  features: features.length, kb,
                  licence: 'Natural Earth — public domain' });
}

await writeFile(join(ROOT, 'derived', 'manifest.json'),
                JSON.stringify(manifest, null, 1));
console.log('  manifest written');
