# map_engine — a programmable educational map animation engine

Scene YAML in, MP4 out. No model is involved at any point: the same scene file
produces the same pixels every run.

    node map_engine/data/fetch.mjs                     # once, gets the datasets
    node map_engine/renderer/render_map.mjs \
         map_engine/scenes/1857_meerut_delhi.yaml \
         --output map_engine/output/1857.mp4 \
         --width 1080 --height 1920 --fps 30 [--theme textbook] [--debug]

## Why a browser and not Python/GeoPandas

Three reasons, in order of weight.

**Devanagari.** Labels are the point of an educational map, and complex-script
shaping is the thing this repo has already been burned by — Pillow without
libraqm silently reorders matras (विद्युत् → वदि्युत्). Matplotlib has the same
class of problem. Chromium shapes Devanagari correctly.

**It is already here.** `tools/edu/renderer` runs Playwright and pipes JPEG
frames straight into ffmpeg. The map engine reuses that shape exactly, and the
Devanagari fonts are already installed.

**Disk.** geopandas/fiona/pyproj/cartopy pulls GDAL. This machine had 3.2 GB
free when the engine was written, and a build has died of a full disk before.
d3-geo is 8 packages.

## Layout

    data/fetch.mjs          downloads Natural Earth and TRIMS it before storing
    data/derived/           the trimmed GeoJSON actually used (1.1 MB, not 45)
    data/locations/         the location registry — scenes say "Meerut"
    data/LICENSES.md        every dataset's licence, and the India boundary note
    themes/textbook.yaml    all colour and line weight; none of it is in the code
    scenes/                 scene files
    renderer/map.html       the render surface: d3-geo + SVG
    renderer/lib/camera.mjs zoom<->scale, easing, fitBounds
    renderer/lib/scene.mjs  parsing and validation
    renderer/lib/timeline.mjs  state as a pure function of t
    renderer/render_map.mjs the CLI
    output/                 generated; gitignored

## Scene schema

    scene: { id: <string>, duration: <seconds> }
    map:
      base: India                  # what the opening camera fits, if no viewport
      viewport: { center: [lon, lat], zoom: 4.5 }     # optional, overrides base
      layers: { states: true, rivers: false, lakes: false }
      actions:
        - { time: 0,   type: show_map }
        - { time: 1,   type: fly_to,    location: Meerut, zoom: 8.2, duration: 2 }
        - { time: 3.2, type: point,     location: Meerut, label: "मेरठ" }
        - { time: 5,   type: route,     from: Meerut, to: Delhi, duration: 2.2 }
        - { time: 10,  type: fly_to,    location: India, duration: 2.4 }
        - { time: 12,  type: highlight, feature: "Madhya Pradesh" }

`location` resolves against the registry first, then against feature names in
the map data — so `fly_to: India` or `fly_to: "Madhya Pradesh"` fits that
polygon's bounds and needs no zoom.

## Two rules the engine keeps

**Things persist once they appear.** A point stays, a drawn route stays. The
student is still looking at Meerut while the teacher talks about Delhi.
Removal will be an explicit action, never a side effect of time passing.

**Validation refuses rather than guesses.** A scene naming a place the registry
does not have is a scene whose author believed something false; centring on
Delhi instead would hide that. All faults are reported at once, and the process
exits 1.

## Not built yet

Deliberately, so the foundation could be proven first: label collision
avoidance, `remove` actions, districts, choropleth/data layers, legends,
arrowheads on routes, custom GeoJSON layers, transparent/alpha output, PNG
sequence export, and the caching of rendered basemaps.
