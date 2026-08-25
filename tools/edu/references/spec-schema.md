# `spec/segments.json` — schema aur rules

Ek array, har segment ek object. Ye file poore video ka **single source of truth** hai.

```jsonc
{
  "seg_id": 4,
  "type": "TEXT_ONLY | DIAGRAM | EQUATION | DIAGRAM_EQUATION",
  "duration": 10.0,
  "voiceover": "exact Hinglish line — HeyGen isi ko bolega",

  "phrases": [
    { "text": "Screen par verbatim yahi aayega",
      "golden": "verbatim",          // exactly ek word gold, ya null
      "t_in": 0.0, "t_out": 4.8 }
  ],

  "diagram": {
    "asset": "assets/metal-lattice.svg",
    "carry_over": ["ions", "e_sea"],   // frame 0 se visible, fade-in nahi
    "timeline": [
      { "id": "free_e", "action": "pop_in", "t": 7.9, "dur": 0.6 }
      // actions: fade_in fade_out pop_in pop_out move draw pulse
      // move ke liye: "to": [dx, dy]  (SVG user units)
      // optional "ease": ease_out (default) | smooth | linear |
      //                  rush_from | rush_into | there_and_back
      //                  -> references/animation-craft.md dekho
    ]
  },

  "labels": [
    { "text": "4s", "x": 0.141, "y": 0.720, "t_in": 1.5, "accent": false }
    // x = 0–1 frame width, y = 0–1 STAGE height (470px), t_in = -0.6 -> already present
  ],

  "equation": {
    "latex": "\\Phi_E = \\dfrac{q}{\\varepsilon_0}",
    "t_in": 1.8,
    "highlight": { "t": 6.2, "latex": "...\\textcolor{#FFC53D}{q}..." }
  },

  "end_state": ["ions", "e_sea"],   // = agle segment ka carry_over
  "editor_note": "editor me kya karna hai — spec me nahi ja sakta"
}
```

---

## Timing — word-budget se nikalo, equal thirds se NAHI

Voiceover ~2.8 words/sec bolta hai. Equal thirds dene par lamba phrase apne slot me
fit nahi hota aur text awaaz se aage-peeche ho jata hai.

```
phrase duration = (phrase ke spoken words ÷ segment ke total words) × 9.6 s
```
Phir har phrase ke beech **0.2 s gap**, last phrase **exactly `duration` par** khatam.

Example — 21-word segment, chunks 8 + 6 + 7 words:
`0.0–3.7` · `3.9–6.6` · `6.8–10.0`

### Hard rules
| Rule | Kyun |
|---|---|
| `t_out − t_in` ≥ **2.5 s** | padhne ka time |
| Do phrases ke beech **exactly 0.2 s** | flicker se bachne ke liye |
| Pehla `t_in` = **0.0**, aakhri `t_out` = `duration` | gap na rahe |
| Phrase ≤ **10 words** | 3 line se zyada nahi |
| Segment N ka `end_state` = N+1 ka `carry_over` | continuity |
| `t + dur` ≤ **10.0** har timeline step me | clip se bahar na jaye |
| Label `t_in` ≤ 9.6 | dikhne ka time mile |

---

## `golden` word
- **Exactly ek** word gold hota hai, ya `null`
- Phrase me maujood hona chahiye, verbatim
- Hyphen/apostrophe wala word mat chuno (`d-block` ❌) — engine hyphen ko U+2011
  non-breaking me badalta hai, match toot jata hai
- **Phrase me koi math symbol (`+`, `=`, `(`, `)`, `−`) ho to `golden: null`**

## Hyphen ka jaal
Engine `d-block`, `d-orbital`, `(n-1)d` ke hyphen ko U+2011 me badal deta hai taaki line
na toote. `render.mjs`/`full.mjs` ka audit dono ko normalise karke compare karta hai.
Naya audit code likho to ye normalise mat bhoolna, warna jhoota `TEXT MISMATCH` aayega.

## `carry_over` vs `timeline`
- `carry_over`: pichle segment se chali aa rahi cheezein — **frame 0 se poori visible**,
  koi entry animation nahi. Warna har segment me diagram dobara banta dikhega.
- `timeline`: is segment me jo naya aa raha hai.
- Naya diagram aa raha ho (alag asset) to purane ko is segment ke ~8.8 s par `fade_out`
  kar do, warna do diagram overlap karte hain.

## Object entry timing
Koi object uska naam bole jaane ke **0.4–1.5 s baad** aana chahiye. Pehle aa gaya to
distraction, baad me aaya to disconnect.

## Labels ke coordinates
`x` frame width ka fraction (0–1), `y` **stage height** (470px) ka fraction.
Label diagram ke element ke upar na chadhe — render karke frame dekh kar adjust karo.
