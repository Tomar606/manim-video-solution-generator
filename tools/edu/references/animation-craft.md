# Animation craft

Manim-video-generator ke `skills/` folder se nikaali gayi animation knowledge, is
pipeline ke hisaab se dhali hui. Manim ke Python calls yahan kaam ke nahi — lekin
uske peeche ke **timing, staging aur revelation principles** seedhe hamare
`diagram.timeline` par lagte hain.

Credit: Rohit Ghumare ka manim-video-generator, aur Manim Community.

---

## 1. Progressive revelation — sabse bada principle

> **Sab kuch ek saath kabhi mat dikhao.** Perat dar perat banao, taaki dekhne wala
> har tukda samajh le usse pehle ki agla aaye.

Teen level me socho, aur isi order me screen par laao:

| Level | Kya | Kab |
|---|---|---|
| **1 — Essential** | Asli cheez, bina jiske baat hi nahi banti | pehle |
| **2 — Supporting** | Usko explain karne wale hisse, labels | uske baad |
| **3 — Enriching** | Highlight, ring, extra arrow | sabse aakhir |

Galvanic cell ka example — yahi order timeline me hai:
`beakers` (L1) → `electrodes` (L1) → `salt_bridge` (L1) → `wire` + `bulb` (L2)
→ `e_flow` (L2) → `bulb_glow` (L3, jab "spontaneous" bola jaata hai)

**Revelation patterns:**
- **Linear** — step 1, phir step 2 jo step 1 par bana hai (derivation, process)
- **Central expansion** — beech ki cheez pehle, phir uske aas-paas wali (atom, cell)
- **Layer stacking** — neeche se upar (energy levels, lattice)
- **Question → answer** — sawal dikhao, ruk jao, phir jawab (hook segments)

---

## 2. Duration defaults

Manim ki durations, hamare actions par mapped:

| Kya ho raha hai | Action | `dur` |
|---|---|---|
| Line/shape ban rahi hai | `draw` | 0.8 – 1.1 |
| Cheez aa rahi hai | `fade_in` | 0.4 – 0.5 |
| Cheez ja rahi hai | `fade_out` | 0.4 |
| Zor dekar aa rahi hai | `pop_in` | 0.35 – 0.45 |
| Jagah badal rahi hai | `move` | 0.6 – 0.9 |
| Dhyaan kheenchna hai | `pulse` | 2.0 – 3.0 |

**Educational pacing = default se ~1.5x dheema.** Ye reel padhane ke liye hai,
dikhane ke liye nahi. Jaldi wali animation samajh nahi aati.

**Staggered reveal:** ek jaisi cheezein ek saath mat laao — **0.3–0.4 s ke antar**
se laao (Manim ka `LaggedStart`). Jaise oxidation ladder ke rungs 0.4 s apart, ya
lattice ke ions. Ek saath aane par "phat" pad jata hai, ek-ek karke aane par aankh
follow karti hai.

---

## 3. Rate functions (`ease`)

Har timeline action par optional `"ease"` field. Default `ease_out` — purane spec
waise hi chalte rahenge.

| `ease` | Curve | Kab use karo |
|---|---|---|
| `ease_out` | tez shuru, dheema ant | **default**, zyadatar cheezein |
| `smooth` | dheema–tez–dheema | natural movement, `move` actions |
| `linear` | ek raftaar | current, electron flow, mechanical cheezein |
| `rush_from` | tez shuru, dheema ruk | wazan ke saath aana |
| `rush_into` | dheema shuru, tez ant | nikalna, kheencha jana |
| `there_and_back` | 0 → 1 → 0 | zor dena bina state badle |

```jsonc
{ "id": "e_flow", "action": "fade_in", "t": 4.6, "dur": 0.5, "ease": "linear" }
```

Rang ki tarah — **ease ka matlab hona chahiye, sajawat nahi.** Shak ho to default rehne do.

---

## 4. Composition

**Screen regions** hamare me pehle se locked hain (text 100–340, diagram 380–850,
avatar 960+). Manim ka `to_edge` wala kaam yahan `style.css` ne kar diya hai.

**Visual hierarchy:** size aur colour se banao, position se nahi. Jo sabse zaroori
hai wo sabse mota/chamakdaar ho. Ek frame me **do se zyada** "dekho mujhe" cheezein
mat rakho.

**Act structure**, 10-second segment ke andar:
- 0 – 2 s — context (caption aata hai, stage abhi khaali reh sakta hai)
- 2 – 7 s — main build (diagram banta hai)
- 7 – 10 s — reinforce (highlight, ring, pulse)

---

## 5. Emphasis — sabse halka tareeka jo kaam kar jaye

Zor dene ke tareeke, kam se zyada dakhal ke hisaab se:

1. **Colour** — accent gold (`accent: true` label)
2. **Pulse** — `there_and_back`, state nahi badalta
3. **Ring / outline** — `cmp_ring`, `d_ring` jaisa
4. **Baaki sab halka karo** — asli emphasis: focus wali cheez chhodkar sab fade

Pehla jo kaam kar jaye wahi use karo. Teen emphasis ek saath = koi emphasis nahi.

---

## 6. Manim khud kyun use nahi kar rahe

Repo achhi hai, par uska render path is pipeline ke liye ulta padega:

| | Manim repo | Ye pipeline |
|---|---|---|
| Code kaun likhta hai | **OpenAI** Manim Python generate karta hai | Diagram hath ka likha SVG |
| Galti ka rasta | AI galat equation/label bana sakta hai | Text spec se aata hai, audit hota hai |
| Install | Python + Manim CE + LaTeX (~4 GB) + FFmpeg | Node + FFmpeg |
| Frame | 16:9 math scene | 9:16 locked zones, avatar ka aadha khaali |
| Verify | koi guarantee nahi | `validate.py` + `qa.mjs` + text audit |

AI se code likhwana **wahi bug-class wapas laata hai** jise hatane me itni mehnat
lagi — galat spelling, ulta concept, double symbol. Isliye render path deterministic
hi rahega.

Manim tab socho jab kabhi **3D surface, vector field, ya continuous math
transformation** chahiye ho — wahan SVG kaafi nahi padega. Us case me wo clip alag
se banao aur editor me daalo, poora pipeline mat badlo.
