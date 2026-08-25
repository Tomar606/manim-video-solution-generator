# Diagram SVG banane ke rules

Diagram AI generate nahi karta. Ye `assets/*.svg` me hand-written files hain. Isi wajah
se wo 100% accurate aur har baar same rehte hain.

---

## 7 hard rules

1. **`<text>` element kabhi nahi.** Har shabd/number spec ke `labels` se aata hai —
   tabhi audit verify kar pata hai ki jo likha tha wahi screen par aaya. Comment me bhi
   `<text` mat likho, validator confuse ho jata hai.
2. **viewBox hamesha `0 0 1080 470`.** Stage exactly itna hi hai.
3. **Har animate hone wale part ka apna `id`.** Group `<g id="...">` me rakho.
4. **`data-optional` lagao** har optional group par — jo part spec me reference nahi
   hua, engine use chhupa deta hai. Ek SVG kai segments me alag reveal ke saath chalega.
5. **Straight line par gradient stroke kabhi nahi.** Horizontal/vertical line ka
   bounding box zero-height hota hai, `objectBoundingBox` gradient invisible render
   hota hai. **Solid stroke** use karo.
6. **Mote strokes.** 1080×470 ko phone par dekha jata hai. Line ≥ 6px, main bar 14–18px,
   circle radius ≥ 14. Patli lines chalkboard par gayab ho jati hain.
7. **Frame bharo.** x 150–950, y 70–400 use karo. Chhota diagram beech me tairta hua
   bura lagta hai.

---

## Colours (`style.css` ke tokens se match karo)

| Use | Hex |
|---|---|
| Diagram stroke, s-orbital, "first" cheez | `#7FD4FF` cyan |
| Accent, d-orbital, "important" cheez | `#FFC53D` gold |
| Soft accent / bracket | `#EDC68A` |
| Dim context (jo focus me nahi) | `#5C6B7A` |
| Positive charge | `#FF5A5A` |
| Heat / warm | `#FF7A45` |
| Dark fill (circle ke andar) | `#12283A` (cyan par), `#2A1E05` (gold par) |

**Colour ka matlab hona chahiye, sajawat nahi.** Ek diagram me 2–3 se zyada rang mat do.

---

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 470">
  <!-- Ek line me science: ye diagram kya sikha raha hai.
       No text elements: every label comes from the spec. -->

  <g id="context" data-optional>
    <!-- jo dim rehna hai -->
  </g>

  <g id="main_thing" data-optional>
    <!-- asli cheez, mote strokes -->
  </g>

  <g id="highlight" data-optional>
    <!-- jo baad me pop hoga -->
  </g>
</svg>
```

---

## Repetitive parts Python se banao

Grid, lattice, ladder — haath se mat likho. Python se generate karo, galti nahi hogi:

```python
cells = [f'<rect x="{X0+c*48}" y="{Y0+r*40}" width="44" height="36" rx="5" '
         f'fill="none" stroke="#5C6B7A" stroke-width="2"/>'
         for r in range(7) for c in cols_for_row(r)]
```

---

## Maujooda library

| File | ids | Kis kaam ka |
|---|---|---|
| `dblock-orbitals.svg` | `s_box` `d_boxes` `s_electrons` `flying_e` `d_electron` `d_ring` `d_partial` `empty_mark` `boxFill` `eGlow` | orbital boxes, electron filling |
| `oxidation-ladder.svg` | `axis` `ox2`–`ox7` | oxidation states ki seedhi |
| `energy-levels.svg` | `energy_axis` `ns_level` `nd_level` `gap_bracket` `e_ns` `e_nd` `bond_arrows` | do energy levels lagbhag same + bonding |
| `metal-lattice.svg` | `e_sea` `ions` `ion_charge` `free_e` `slip_layer` | metallic bonding, malleable/ductile |
| `conductivity.svg` | `bar` `e_flow` `flow_arrow` `heat` | heat + electricity conduction |
| `periodic-dblock.svg` | `pt_grid` `d_cells` `d_outline` | periodic table me d-block ki jagah |
| `gauss-sphere.svg` | `charge` `field` `sphere` `radius` `dA_patch` `arrow` | Gauss law, electric field |
| `galvanic-cell.svg` | `beakers` `electrode_L` `electrode_R` `salt_bridge` `wire` `bulb` `bulb_glow` `e_flow` `sign_minus` `sign_plus` | Galvanic cell: 2 beakers + salt bridge + bulb. Anode LEFT (−), cathode RIGHT (+) |
| `electrolytic-cell.svg` | `vessel` `electrode_A` `electrode_C` `wires` `battery` `e_flow` `sign_plus_A` `sign_minus_C` | Electrolytic cell: ONE vessel + battery. Anode LEFT (+), cathode RIGHT (−) |
| `energy-flow.svg` | `g_row` `g_arrow` `e_row` `e_arrow` | Do rows: chemical→electrical aur electrical→chemical |
| `gibbs-arrows.svg` | `baseline` `g_down` `e_up` | ΔG neeche (spontaneous) vs upar (non-spontaneous) |
| `compare-cells.svg` | `divider` `cmp_g` `cmp_bridge` `cmp_ring` `cmp_e` `cmp_cross` | Dono cells side-by-side, salt bridge hai/nahi |

Naya SVG banao to is table me add karo.

---

## Banane ke baad HAMESHA dekho

```bash
CHROME_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome node full.mjs <seg>
ffmpeg -v error -ss 9.2 -i out/full-video.mp4 -frames:v 1 -vf scale=460:-1 /tmp/c.png -y
```
Phir `view` tool se `/tmp/c.png` kholo.

**Pehli koshish me ye galtiyan aam hain** (mere saath hui hain):
- Bars/lines bahut patli — dikhti hi nahi
- Diagram bahut chhota, 470 height ka aadha bhi use nahi
- Label diagram ke element par chadh gaya
- Circle line ke end se bahar nikal gaya

Ye sirf render karke dekhne se pata chalta hai. Validator ye nahi pakadta.
