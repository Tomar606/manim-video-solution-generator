# Arivihan — Truth Layer Pipeline (Option A)

Upper 50% ab code se banega, Veo se nahi. Text, labels, equations aur diagram deterministic hain — jo JSON me likhoge, bilkul wahi frame par aayega. Har baar. Veo sirf background motion banayega, aur usme ek bhi akshar nahi hoga.

**Isse ye 5 bug-classes structurally khatam ho jaate hain:**

| Purana bug | Ab kyun nahi hoga |
|---|---|
| `+` / number double aa jaana | Text DOM node se aata hai, model se nahi |
| Animation ulta chalna | `setTime(t)` ek pure function hai — reverse ka concept hi nahi |
| Text pehle, animation baad me | Dono ek hi timeline se, 33ms precision par |
| Label ka naam galat | Label string spec se copy hota hai, verbatim |
| Diagram concept galat | Diagram tumhara apna SVG hai, generate nahi hota |

---

## 1. Pipeline

```
                    ┌──────────────────────────┐
   Hinglish script  │   spec/segments.json     │   <- SINGLE SOURCE OF TRUTH
   (word-locked) ──►│   har segment ka poora   │
                    │   sach, ek jagah         │
                    └────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
   GATE 1: SME review     node render.mjs         node bg-prompts.mjs
   (JSON padho, 2 min)    ──────────────►         ──────────────►
   video mat dekho        out/seg-N.mov           Veo prompts
                          ProRes 4444 alpha       (ZERO text)
                          = TRUTH LAYER           = BACKGROUND LAYER
                                 │                      │
                                 └───────┬──────────────┘
                                         ▼
                                  Video editor
                                  bg → truth layer → HeyGen avatar
                                         ▼
                                  GATE 2: final watch
```

Purana process **telephone game** tha: script → diagram prompt → animation prompt → video prompt → Veo. Har hop par fidelity gir rahi thi. Ab ek hi file se dono branches nikalti hain, aur wo file insaan ke padhne layak hai.

---

## 2. Roles

| Kaun | Kya karta hai | Kitna time / video |
|---|---|---|
| Script writer | Hinglish script, word-locked | 20 min |
| Producer | Script → `segments.json` | 25 min (template se) |
| **SME (subject teacher)** | **Gate 1 — sirf JSON padhta hai** | **2 min** |
| Illustrator | Naya diagram SVG (agar library me nahi) | 40 min, **ek baar** |
| Producer | `npm run render` + Veo prompts | 10 min |
| Editor | 3 layer composite | 25 min |

Sabse bada change: **SME ab video nahi dekhta, JSON padhta hai.** Video dekhke bug dhoondhna sabse mehnga QC method hai — 10 min lagta hai aur aadhe bugs chhoot jaate hain. JSON me `"text": "Chaaron taraf closed sphere"` galat ho to 5 second me dikh jaata hai.

---

## 3. SOP — ek video, step by step

### Step 0 — setup (ek baar, 5 min)
```bash
npm install
npx playwright install chromium
```

### Step 1 — script lock karo
- ~18–22 words per 10-sec segment
- Natural pause par kaato, mid-clause kabhi nahi
- 13 segments ka sweet spot rakho

### Step 2 — `spec/segments.json` likho
Har segment ke liye ek object. Schema section 5 me.
- Phrase ≤ ~34 characters ho to bada font, uske upar auto chhota
- `golden` sirf ek simple word — koi apostrophe, hyphen ya math symbol nahi
- Phrase ke andar math symbol ho to `golden: null`

### Step 3 — GATE 1: SME review
SME sirf ye check karta hai:
- [ ] Har `phrase.text` spelling-correct aur concept-correct
- [ ] `voiceover` aur `phrases` ka matlab match karta hai
- [ ] `equation.latex` sahi formula hai
- [ ] `labels` ke naam sahi hain
- [ ] `diagram.timeline` ka order concept ke hisaab se sahi hai (charge pehle, sphere baad me)
- [ ] `end_state` agle segment ke `carry_over` se match karta hai

Yahan approve hua = video sahi banega. Guarantee.

### Step 4 — preview me scrub karo
```bash
npm run preview     # http://localhost:5178/renderer/index.html
```
Dropdown se segment chuno, slider se scrub karo, ▶ se play. Yahi wo jagah hai jahan timing tweak karna hai — render se **pehle**. Ek scrub 15 second leta hai, ek render 90 second.

### Step 5 — render
```bash
npm run render                 # saare segments
node render.mjs 4              # sirf segment 4
node render.mjs 4 --contact    # + 12-frame QC contact sheet
SKIP_PRORES=1 npm run render   # sirf WebM (tez, iteration ke liye)
node snap.mjs 4 6.2            # ek hi frame, 3 second me — timing tune karne ke liye
```
Output `out/` me:
- `seg-N.mov` — ProRes 4444 + alpha → editor me seedha
- `seg-N.webm` — VP9 + alpha → halka, preview/web ke liye
- `seg-N-qc.png` — 12 moments ek image me, 2 second me scan

Script khud text audit chalata hai. Agar spec ka koi string DOM me nahi mila to `TEXT MISMATCH` throw karke non-zero exit deta hai. Chup-chaap galat output nahi jayega.

### Step 6 — Veo background prompts
```bash
npm run bg > out/veo-background-prompts.md
```
Har prompt me hard negative hai — text, letters, numbers, symbols, diagram, sab banned. **Agar generated clip me ek bhi akshar dikhe to clip discard karo, edit me chhupao mat.**

### Step 7 — composite
1. Veo background plate — sabse neeche
2. `out/seg-N.mov` — beech me (already 1080×1920, y=960 ke neeche transparent, zero alignment kaam)
3. HeyGen avatar, keyed — sabse upar, lower 960px me

### Step 8 — GATE 2
Poora video ek baar dekho. Ab sirf background aur avatar sync check karna hai — text kabhi galat ho hi nahi sakta.

---

## 4. Diagram Asset Library — sabse bada leverage

`assets/` me har diagram ek baar banao, hamesha ke liye. **Rules:**

1. **SVG me `<text>` kabhi nahi.** Saare shabd spec se aate hain — tabhi to audit ho paate hain.
2. Har animate hone wala part ka apna `id` ho.
3. `data-optional` lagao — jo part spec me referenced nahi, engine use chhupa deta hai. Ek hi SVG kai segments me alag-alag reveal ke saath chalega.
4. viewBox hamesha `0 0 1080 470`.
5. Horizontal/vertical line par gradient stroke kabhi nahi — zero-height
   bounding box par `objectBoundingBox` gradient invisible render hota hai.
   Solid stroke use karo. (Ye bug oxidation ladder me pakda gaya.)

50 diagram ban gaye = naye video ki lagat aadhi. Ye compounding asset hai, per-video kharcha nahi.

---

## 5. Segment Spec — schema

```jsonc
{
  "seg_id": 4,
  "type": "TEXT_ONLY | DIAGRAM | EQUATION | DIAGRAM_EQUATION",
  "duration": 10.0,
  "voiceover": "exact Hinglish line — HeyGen isi ko bolega",

  "phrases": [
    { "text": "Ek point charge lo",   // screen par verbatim yahi
      "golden": "charge",             // exactly ek word gold, ya null
      "t_in": 0.0, "t_out": 4.8 }
  ],

  "diagram": {
    "asset": "assets/gauss-sphere.svg",
    "carry_over": ["charge"],         // frame 0 se hi visible, fade-in nahi
    "timeline": [
      { "id": "sphere", "action": "fade_in", "t": 6.1, "dur": 0.9 }
      // actions: fade_in fade_out pop_in pop_out move draw pulse
    ]
  },

  "labels": [
    { "text": "+q", "x": 0.50, "y": 0.72, "t_in": 2.0, "accent": false }
    // x = 0–1 frame width, y = 0–1 stage height
  ],

  "equation": {
    "latex": "\\Phi_E = \\dfrac{q}{\\varepsilon_0}",
    "t_in": 1.8,
    "highlight": { "t": 6.2, "latex": "...\\textcolor{#FFC53D}{q}..." }
  },

  "veo_background": "background clip ka description — sirf motion aur light",
  "end_state": ["charge", "field", "sphere"]   // agle segment ka carry_over
}
```

**Non-negotiables:**
- `t_out` – `t_in` ≥ 2.5s (padhne ka time)
- Do phrases ke beech 0.2s gap (`t_out: 4.8` → `t_in: 5.0`)
- Object ki entry uske naam ke on-screen hone ke 0.4–1.5s baad
- Segment N ka `end_state` = segment N+1 ka `carry_over`

---

## 6. Migration plan

| Week | Kya |
|---|---|
| 1 | Ek purana video is pipeline se dobara banao. Side-by-side compare karo. |
| 2 | Top 10 chapters ke diagram SVG bana lo. Producer ko spec likhna sikhao. |
| 3 | Naye videos default is pipeline par. Veo sirf background ke liye. |
| 4 | `video-prompt` skill ko update karo — ab wo Veo prompts ki jagah `segments.json` output kare. Bug-ledger ke jo rules text/count/order ke baare me the, wo delete ho jayenge — engine unhe structurally handle karta hai. |

**Track karo:** regenerations per segment (target **0**), minutes per finished video, Gate-2 rejection rate.

---

## 7. Files

```
spec/segments.json     tumhara kaam — har video ka sach
assets/*.svg           diagram library — ek baar banao, hamesha use karo
renderer/style.css     design tokens (colour, type, layout zones)
renderer/engine.js     setTime(t) — frame = pure function of t
renderer/index.html    frame page + preview scrubber
render.mjs             frames capture -> ProRes/WebM + QC sheet
snap.mjs               ek frame at time t — timing tuning ka fastest loop
bg-prompts.mjs         same spec -> zero-text Veo prompts
server.mjs             local static server (preview + render)
```

Design tokens sirf `style.css` ke `:root` me hain. Brand badalna ho to wahin 6 line badlo, saare videos update ho jaate hain.
