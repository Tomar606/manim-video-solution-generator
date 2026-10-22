# Dataset licences and attribution

Every dataset used by the map engine is recorded here. A dataset whose licence
is not compatible with commercial use does not go in, however convenient it is.

## In use

**Natural Earth** — `data/derived/*.geojson`
Public domain. No attribution required, no restriction on commercial use.
Source: https://www.naturalearthdata.com (via nvkelso/natural-earth-vector).
Files are trimmed copies; `data/derived/manifest.json` records the exact source
URL and feature counts for each.

**Natural Earth raster relief** — `data/derived/relief_south_asia_merc.jpg`
Public domain, same terms as the vector data. Cross Blended Hypso with Shaded
Relief and Water, 10m (21600x10800, 1 arcminute). Source:
https://naciscdn.org/naturalearth/10m/raster/HYP_HR_SR_W.zip

Only a South Asia window is kept (lon 50..110, lat -5..48), resampled from
plate carree to Mercator so it can sit under a d3 `geoMercator` projection.
`relief_south_asia.json` records the bounds and the resampling. The 700MB world
GeoTIFF is NOT kept — re-download it from the URL above to rebuild the crop.

A TILE SERVICE WOULD BE EASIER AND IS NOT ALLOWED. Google, Mapbox and Esri
basemaps all restrict commercial redistribution of rendered tiles, which is the
same reason GADM is excluded below. Natural Earth's raster is the only relief
basemap here that can ship in a product.

## Deliberately NOT used

**GADM** — the usual source for Indian district boundaries.
Licensed for **academic and non-commercial use only**. Arivihan is a commercial
product, so GADM cannot be used here even for a single district map.

**Google Maps / Google Earth imagery** — prohibited by terms, and scraping it
is out of the question.

## To be added carefully

**OpenStreetMap** (ODbL) — usable, but requires attribution ("© OpenStreetMap
contributors") visible in or with the video, and share-alike applies to derived
*databases*. A rendered map frame is a Produced Work, so the video itself is
fine with attribution; a redistributed GeoJSON extract would carry ODbL.

**Survey of India** open data — the correct source for Indian administrative
boundaries as India officially depicts them. See the boundary note below.

## The India boundary — READ THIS BEFORE PUBLISHING

Natural Earth depicts India along the de-facto Line of Control, NOT along the
boundary India officially claims. Measured in the trimmed data:

    Ladakh polygon            reaches 79.62 E / 35.50 N  — Aksai Chin excluded
    Jammu and Kashmir polygon reaches 34.77 N            — Gilgit-Baltistan excluded
    India country polygon     reaches 35.50 N            — official claim is ~37.1 N

It also carries a separate "Siachen Glacier" polygon, which India treats as
part of Ladakh.

Publishing a map of India inside India with a non-Survey-of-India boundary is a
legal and reputational risk for an Indian education company. The engine
therefore treats the India outline as REPLACEABLE: drop a Survey-of-India
consistent polygon at `data/custom/india_soi.geojson` and set
`india_boundary: soi` in config/engine.yaml. Until that file exists the engine
renders the Natural Earth outline and prints a warning on every run.
