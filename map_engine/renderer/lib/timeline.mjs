/**
 * The timeline: given the actions and a time t, what is on screen.
 *
 * Written as a PURE FUNCTION of t rather than as a running animation. Frames
 * can then be rendered in any order, a scene can be re-rendered from the
 * middle while debugging, and — the point of the whole engine — the same
 * scene produces the same pixels every time.
 *
 * THINGS PERSIST ONCE THEY APPEAR. A point that has been introduced stays;
 * a route that has been drawn stays drawn. That is the educational default
 * from the brief, and it is also what makes a map readable: the student is
 * still looking at Meerut while the teacher talks about Delhi. Removal is an
 * explicit action, never a side effect of time passing.
 */
import { lerpCamera, zoomToScale, fitBounds } from './camera.mjs';

const clamp01 = x => Math.max(0, Math.min(1, x));

/** Great-circle samples between two points, so a long route bends as it should. */
export function routeCoords(a, b, n = 96) {
  const toR = d => d * Math.PI / 180, toD = r => r * 180 / Math.PI;
  const [lon1, lat1] = [toR(a[0]), toR(a[1])], [lon2, lat2] = [toR(b[0]), toR(b[1])];
  const d = 2 * Math.asin(Math.sqrt(
    Math.sin((lat2 - lat1) / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin((lon2 - lon1) / 2) ** 2));
  if (!d) return [a, b];
  const out = [];
  for (let i = 0; i <= n; i++) {
    const f = i / n;
    const A = Math.sin((1 - f) * d) / Math.sin(d), B = Math.sin(f * d) / Math.sin(d);
    const x = A * Math.cos(lat1) * Math.cos(lon1) + B * Math.cos(lat2) * Math.cos(lon2);
    const y = A * Math.cos(lat1) * Math.sin(lon1) + B * Math.cos(lat2) * Math.sin(lon2);
    const z = A * Math.sin(lat1) + B * Math.sin(lat2);
    out.push([toD(Math.atan2(y, x)), toD(Math.atan2(z, Math.hypot(x, y)))]);
  }
  return out;
}

export function makeTimeline(parsed, { width, height, bounds, start }) {
  const { actions } = parsed;
  const cams = [{ t: 0, cam: start }];          // camera keyframes
  const statics = [];                            // points, routes, highlights

  const camFor = place => {
    if (place.kind === 'point') return null;     // needs an explicit zoom
    const bb = bounds(place.name);
    return bb ? fitBounds(bb, width, height) : null;
  };

  for (const a of actions) {
    if (a.type === 'fly_to' && a.center) {
      cams.push({ t: a.time, dur: a.duration,
                  cam: { center: a.center, zoom: a.zoom } });
    } else if (a.type === 'fly_to') {
      const fitted = camFor(a._place);
      const target = a._place.kind === 'point'
        ? { center: [a._place.lon, a._place.lat], zoom: a.zoom ?? 7 }
        : { center: fitted.center, zoom: a.zoom ?? fitted.zoom };
      cams.push({ t: a.time, dur: a.duration, cam: target });
    } else if (a.type === 'point') {
      statics.push({ kind: 'point', t: a.time, dur: a.fade ?? 0.45,
        lon: a._place.lon, lat: a._place.lat,
        label: a.label ?? (a._place.rec ? a._place.rec.name_hi : null),
        small: !!a.small });
    } else if (a.type === 'route') {
      statics.push({ kind: 'route', t: a.time, dur: a.duration,
        coords: routeCoords([a._from.lon, a._from.lat], [a._to.lon, a._to.lat]) });
    } else if (a.type === 'highlight') {
      for (const f of (a.features || [a.feature]).filter(Boolean))
        statics.push({ kind: 'highlight', t: a.time, dur: a.fade ?? 0.6, feature: f });
    }
  }
  cams.sort((x, y) => x.t - y.t);

  return function stateAt(t) {
    // camera: the last keyframe that has started, eased from the one before
    let cam = cams[0].cam;
    for (let i = 1; i < cams.length; i++) {
      const k = cams[i];
      if (t < k.t) break;
      const prev = cams[i - 1].cam;
      cam = lerpCamera(prev, k.cam, k.dur ? (t - k.t) / k.dur : 1);
    }
    const points = [], routes = [], highlights = [];
    for (const s of statics) {
      if (t < s.t) continue;
      const f = clamp01(s.dur ? (t - s.t) / s.dur : 1);
      if (s.kind === 'point')
        points.push({ lon: s.lon, lat: s.lat, label: s.label, small: s.small,
                      opacity: f, scale: 0.6 + 0.4 * f });
      else if (s.kind === 'route') routes.push({ coords: s.coords, frac: f });
      else highlights.push({ feature: s.feature, opacity: f });
    }
    return { camera: { center: cam.center, zoom: cam.zoom, scale: zoomToScale(cam.zoom) },
             points, routes, highlights };
  };
}
