# Backgrounds library

Background plates, textures and B-roll photographs for the portrait (1080x1920)
Hindi PYQ explainers. Every file here has a recorded licence in `manifest.json`.
**A file with no licence entry is not shippable.** If you add a file, add its
entry.

Total size: about 180 MB (cap: 400 MB). Built 8 Oct 2026.

## What's here

```
backgrounds/
  manifest.json            one entry per file (277): id, file, kind, subject, topic, tags,
                           suits_skins, width, height, orientation, source_site, page_url,
                           download_url, author, licence, licence_url, credit_required,
                           credit_line, notes
  plates/
    earth/source/          17 NASA earth images, <=4000 px long edge (night lights + true colour)
    earth/portrait/        19 ready-made 1080x1920 crops of those
    generated/             19 clean 1080x1920 skin bases we made ourselves (Pillow/numpy)
    textures/              23 CC0 colour maps at 2K (ambientCG, Poly Haven), seamless
    textures/commons/      7 paper textures from Wikimedia Commons (ruled, graph, torn, aged)
  photos/<subject>/<topic>/  191 B-roll photos, <=2400 px long edge, JPEG q85,
                           each folder with a credits.json in tools/fetch_photos.py format
  previews/                contact sheets: plates.jpg and one sheet per subject
```

### Plates per skin

| Skin | Generated bases | Also suits |
|---|---|---|
| night-hud | `night-hud-base-glow`, `-grid`, `-starfield` | all 36 earth plates (night ones are the main use) |
| paper-editorial | `paper-editorial-cream`, `-cream-deep`, `-dotgrid` | paper, kraft, plaster and aged-paper textures; day earth plates as duotone |
| chalk-slate | `chalk-slate-green`, `-black`, `-green-smudged` | (no photographed chalkboard; see gaps) |
| blueprint | `blueprint-grid`, `-grid-dark`, `-plain` | `commons-graph-paper-notepad` |
| newsprint-mono | `newsprint-mono-light`, `-halftone`, `-dark` | concrete and plaster textures, aged paper |
| pastel-notebook | `pastel-notebook-ruled`, `-mint-dots`, `-lavender-graph`, `-blush-gradient` | fabric textures, ruled and graph paper |

The generated plates have no vignette. Licence: "original (Arivihan)".

### Earth imagery (NASA, US public domain)

- **World at night:** Black Marble 2016 and DMSP 1994–95 city lights. Each has an Asia crop, and DMSP also has a Europe–Africa crop.
- **Asia at night:** the Asia and Middle East 2016 globe.
- **India at night:** VIIRS 2012 (central and east crops), the VIIRS portrait (south crop), Diwali 2012, and South India with Sri Lanka.
- **India at night, from the ISS:** Northern India, Delhi under stars, and the west coast.
- **Day:** two Blue Marble globes, two ISS Himalaya shots, India–Maldives coast, and two orbital sunrises.

**Boundary rule.** None of these images has a drawn political boundary. But in three full-frame India night images the floodlit India–Pakistan border fence shows up at full resolution as a thin lit line in the north-west: `night-india-viirs-2012`, `night-india-viirs-portrait` and `night-india-diwali-2012`. Use the provided portrait crops, which leave that area out, and never present the full frame as a map of India. I deleted `ISS-62 City lights of western India and Pakistan` because the fence is prominent in it. The manifest `notes` field records this per file.

### Photos per subject / topic (191)

| Subject | Count | Topics (photos each) |
|---|---|---|
| geography | 64 | rivers 4, rice-paddy-farming 5, thar-desert 4, himalaya 4, plateau 3, coastline 5, city-crowd 3, city-skyline 4, factories-industry 4, mining 5, railways-freight 4, ports 4, villages 4, deforestation 4, irrigation 4, soil 3 |
| political-science | 32 | parliament 3, rashtrapati-bhavan 4, supreme-court 3, voting-elections 5 (ink finger, EVM, VVPAT), rallies-protests 2 (Kolkata human chain and a women's march), constitution 3, nepal 4, un-assemblies 5, newspapers 3 |
| history | 9 | freedom-movement 5 (two PD Salt March photos, Jallianwala Bagh memorial x2, Gohpur Quit India martyrs' statue), monuments-archival 4 (Red Fort, India Gate, Gateway of India) |
| economics | 23 | mandi-markets 5, banks 3, farmers 4, factories-labour 5, shops 6 |
| chemistry | 20 | lab-glassware 6, chemistry-demos 5, electrolysis-batteries 4, rust-corrosion 5 |
| biology | 26 | plants-leaves-flowers 7, pollination 5, microscope 4, cells-micrographs 5, human-body-medical 5 |
| physics | 17 | magnets 5, electric-circuits 4, power-lines-generators 4, solar-panels 4 |

Orientation: 147 landscape, 41 portrait, 3 square.

## How to use

- **Full bleed.** Scale to cover 1080x1920 (crop, never letterbox), then grade per skin:
  - **night-hud:** darken to 35–50% brightness, cool the shadows towards navy, keep highlights so city lights glow.
  - **paper-editorial:** duotone. Convert to luma and map shadows to the skin's red (or blue) ink and highlights to the cream paper colour, with a coarse halftone screen over the top. Set it on a `paper-editorial-*` plate.
  - **newsprint-mono:** greyscale, raise contrast, add halftone, and multiply onto `newsprint-mono-light`.
  - **chalk-slate / blueprint / pastel-notebook:** photos are an accent here. Use them small, framed, or duotoned in the skin's line colour. The generated plate stays the background.
- **Content stays in the top 60%**, where the presenter cutout won't cover it. Choose a crop whose subject sits in that band, or place the photo so it does.
- **Textures** under `plates/textures/` are seamless 2K tiles. Tile them or scale up 1.5× to cover 1080x1920. The Commons paper textures are not seamless.
- **Finding things:** filter `manifest.json` by `subject`, `topic`, `kind`, `suits_skins` or `tags`. The previews in `previews/` are for browsing by eye.

## Credit obligations

| Licence | Files | What you must do |
|---|---|---|
| Public domain (NASA, US government, old archival) | 51 | Nothing required. "Image: NASA" is courteous on earth plates. |
| CC0 (ambientCG, Poly Haven, some Commons) | 38 | Nothing required. |
| original (Arivihan) | 19 | Nothing. |
| CC BY 2.0 / 3.0 / 4.0 | 35 | **Credit the author and licence.** Use `credit_line` from the manifest, in the end card or the video description. |
| CC BY-SA 2.0 / 2.5 / 3.0 / 4.0 | 134 | **Credit the author and licence.** ShareAlike also applies to the modified image itself (a crop or duotone of it): that derivative must be offered under the same CC BY-SA licence. Shipping it inside a video is generally fine; say so in the credits. |

`credit_required` is true on every CC BY and CC BY-SA entry. Some items carry no legal duty to credit but still have a courtesy credit line, such as the Wellcome Collection and USAID images and the NASA plates.

I used only Wikimedia Commons licences that allow commercial use and modification (CC0, PD, CC BY, CC BY-SA). There is no NC or ND licence, no stock site, and no Unsplash or Pexels file here.

## How this was built (and a Commons gotcha)

- Photos were found through the Commons search API with the same licence filter as `tools/fetch_photos.py`.
- **Commons thumbnail rule (2025 onwards).** Commons now serves thumbnails only at its listed widths:
  - 1280, 1920 and 3840 work.
  - 1600, 2400, 2560 and 4000 return **HTTP 400** ("Use thumbnail sizes listed on https://w.wiki/GHai").
  - Bulk downloads of *original* files get **HTTP 429** almost immediately.
- `tools/fetch_photos.py` asks for `iiurlwidth=1600`. The thumbnail URL it receives will be rejected, or for files ≤1600 px wide it falls back to the original and gets rate limited. I did not edit the repo tool. My fetch scripts asked the API for 1920 thumbnails and downloaded only the 1920 or 3840 buckets, building the `/thumb/.../1920px-` URL from the original's path when the API returned an unscaled one. **Fix needed in `tools/fetch_photos.py`:** change `iiurlwidth` to `"1920"`.
- Every candidate was reviewed on a contact sheet. I removed these:
  - maps (one was a district map)
  - engravings, paintings and infographics
  - wrong subjects (the Australian, Singaporean and Swiss parliament buildings, a rock concert)
  - burnt-in date stamps and corner signatures
  - close-up portraits of private individuals
  - a political-party rally stage, kept out to stay neutral
  - near-duplicates
  - one CC BY-SA file with no recorded author

## Gaps (no good free photo found, or thin)

- **rallies-protests (2):** most free protest photos are close-ups of identifiable people, or one party's branding. Generate, or use crowd shots from `geography/city-crowd`.
- **parliament (3):** all three show the old circular Sansad Bhavan (now Samvidhan Sadan). There's no freely licensed photo of the **new Parliament building (2023)** of usable quality.
- **constitution (3):** two Preamble pages (English and Hindi) and one Constituent Assembly group photo. There's no clean close-up of the hand-written manuscript.
- **soil (3):** a red ploughed field, ploughing in Raichur, and an erosion gully (that one is in Ghana, not India). There's no black cotton soil, laterite or soil profile. Generate these, or use textbook figures.
- **city-crowd (3) and Old Delhi:** one strong Old Delhi rickshaw street plus two festival crowds. The Mumbai station crowd shots on Commons were close-ups or watermarked.
- **banks (3):** buildings and branch fronts only. I deliberately avoided currency close-ups.
- **history (9):** few freedom-movement archival photos clear the size floor. The only archival photos are two from the Salt March. The rest are modern memorial photos. There's no archival Quit India, Non-cooperation or 15 August 1947 photo.
- **Nepal:** Kathmandu Durbar Square, Kathmandu valley, Singha Durbar gate and the Nepal parliament (Sansad Bhavan, Kathmandu). There's no Himalaya-from-Nepal shot; use `geography/himalaya`.
- **Chalkboard:** there's no CC0 photographed blank chalkboard, so the chalk-slate skin uses the generated plates only.
- **Torn edges:** there's only one crumpled, torn paper photo, and no alpha-matted torn-edge strips. Make those procedurally if the skin needs them.
- **Unsplash / Pexels:** not used. Their direct download routes need an API key or have no stable licence record per file.
