/**
 * The geographic camera: where the map is looking, and how it gets there.
 *
 * State is (centre, zoom) and nothing else, so a frame is a pure function of
 * time — the same scene renders the same pixels every run, which is the whole
 * point of not generating maps with a model.
 *
 * ZOOM is the slippy-map convention (z=4 sees a subcontinent, z=9 a city), so
 * a scene author's intuition from any web map carries over. The projection
 * scale that d3 wants is derived from it rather than written into scenes.
 */
const TAU = Math.PI * 2;

export const zoomToScale = z => (256 * Math.pow(2, z)) / TAU;

/** Ease in and out. Movement should settle, not arrive at speed. */
export const easeInOutCubic = t =>
  t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

/**
 * Interpolate between two camera states.
 *
 * Longitude and latitude move linearly, but ZOOM MOVES IN LOG SPACE: zoom is
 * an exponent, so a linear walk from 4 to 9 spends most of its time almost
 * fully zoomed in and then lurches. Interpolating the exponent is what makes a
 * fly-to feel even.
 */
export function lerpCamera(a, b, t) {
  const e = easeInOutCubic(Math.max(0, Math.min(1, t)));
  return {
    center: [a.center[0] + (b.center[0] - a.center[0]) * e,
             a.center[1] + (b.center[1] - a.center[1]) * e],
    zoom: a.zoom + (b.zoom - a.zoom) * e,
  };
}

/**
 * The camera that shows all of `bbox` inside width x height, with margin.
 * Used for `location: India` and any other named feature — a scene should be
 * able to say "show Madhya Pradesh" without knowing its coordinates.
 */
export function fitBounds(bbox, width, height, margin = 0.12) {
  const [w, s, e, n] = bbox;
  const lat = y => Math.log(Math.tan(Math.PI / 4 + (y * Math.PI / 180) / 2));
  const dx = Math.abs(e - w) / 360;
  const dy = Math.abs(lat(n) - lat(s)) / TAU;
  const usable = 1 - margin;
  const z = Math.min(Math.log2((width * usable) / (256 * dx)),
                     Math.log2((height * usable) / (256 * dy)));
  return {
    center: [(w + e) / 2,
             (180 / Math.PI) * (2 * Math.atan(Math.exp((lat(s) + lat(n)) / 2)) - Math.PI / 2)],
    zoom: Math.max(0, z),
  };
}
