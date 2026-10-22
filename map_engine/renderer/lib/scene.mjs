/**
 * Scene parsing and VALIDATION.
 *
 * Validation runs before a single frame is drawn, and it refuses rather than
 * guesses. A scene that names a place the registry does not have is a scene
 * whose author believed something false; silently centring on Delhi instead
 * would hide that and ship a map of the wrong country.
 */
import { readFile, readdir } from 'fs/promises';
import { parse } from 'yaml';
import { join } from 'path';

export class SceneError extends Error {}

const norm = s => String(s).trim().toLowerCase();

export async function loadLocations(root) {
  // EVERY file in data/locations, not just india.yaml. A registry that only
  // reads one file quietly ignores the historical places the moment someone
  // adds them, and the scene then fails with "not in the registry" while the
  // author is looking straight at the entry.
  const dir = join(root, 'data/locations');
  const raw = {};
  for (const f of (await readdir(dir)).filter(f => f.endsWith('.yaml')))
    Object.assign(raw, parse(await readFile(join(dir, f), 'utf8')));
  const byKey = new Map();
  for (const [key, v] of Object.entries(raw)) {
    const rec = { key, ...v };
    byKey.set(norm(key), rec);
    if (v.name_en) byKey.set(norm(v.name_en), rec);
    if (v.name_hi) byKey.set(norm(v.name_hi), rec);
  }
  return byKey;
}

export async function loadScene(path, { locations, featureNames }) {
  const doc = parse(await readFile(path, 'utf8'));
  const errs = [];
  const scene = doc.scene || {};
  const map = doc.map || {};
  if (!scene.id) errs.push('scene.id is required');
  if (!(scene.duration > 0)) errs.push('scene.duration must be a positive number');

  const actions = (map.actions || []).map((a, i) => ({ ...a, _i: i }));
  if (!actions.length) errs.push('map.actions is empty — nothing would be drawn');

  const place = (name, where) => {
    const loc = locations.get(norm(name));
    if (loc) return { kind: 'point', lon: loc.lon, lat: loc.lat, rec: loc };
    if (featureNames.has(norm(name))) return { kind: 'feature', name };
    errs.push(`${where}: location "${name}" is not in the location registry `
            + `(data/locations/india.yaml) and is not a feature in the map data`);
    return null;
  };

  for (const a of actions) {
    const at = `action[${a._i}] (${a.type || 'no type'})`;
    if (typeof a.time !== 'number') errs.push(`${at}: time is required`);
    else if (a.time < 0 || a.time > scene.duration)
      errs.push(`${at}: time ${a.time}s is outside the scene's ${scene.duration}s`);
    switch (a.type) {
      case 'show_map': break;
      case 'fly_to':
        // A named place OR a raw centre. The named form is preferred and is
        // what a scene director should emit; the raw form exists because some
        // views are not any one place — the Mauryan centres span from Taxila
        // in modern Pakistan to Karnataka, so "fit India" cuts a centre off.
        if (a.center) {
          if (!Array.isArray(a.center) || a.center.length !== 2
              || a.center.some(v => typeof v !== 'number'))
            errs.push(`${at}: center must be [lon, lat]`);
          else if (Math.abs(a.center[0]) > 180 || Math.abs(a.center[1]) > 90)
            errs.push(`${at}: center [${a.center}] is not a valid coordinate`);
          if (!(a.zoom > 0)) errs.push(`${at}: a center needs an explicit zoom`);
        } else if (!a.location) {
          errs.push(`${at}: needs a location or a center`);
        } else {
          a._place = place(a.location, at);
        }
        if (!(a.duration > 0)) errs.push(`${at}: needs a positive duration`);
        break;
      case 'point':
        if (!a.location) errs.push(`${at}: needs a location`);
        else a._place = place(a.location, at);
        if (a.label !== undefined && !String(a.label).trim())
          errs.push(`${at}: label is present but empty`);
        break;
      case 'route':
        a._from = a.from ? place(a.from, `${at}.from`) : (errs.push(`${at}: needs from`), null);
        a._to = a.to ? place(a.to, `${at}.to`) : (errs.push(`${at}: needs to`), null);
        if (!(a.duration > 0)) errs.push(`${at}: needs a positive duration`);
        break;
      case 'highlight':
        for (const f of (a.features || [a.feature]).filter(Boolean))
          if (!featureNames.has(norm(f)))
            errs.push(`${at}: feature "${f}" is not in the map data`);
        if (!a.feature && !a.features) errs.push(`${at}: needs feature or features`);
        break;
      default:
        errs.push(`${at}: unknown action type "${a.type}"`);
    }
  }
  if (errs.length) throw new SceneError('\n  ' + errs.join('\n  '));
  return { scene, map, actions };
}
