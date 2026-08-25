# START HERE — d-block video

Poori video EK file me. Background, text, diagram, animation — sab andar.
Editor me sirf avatar upar rakhna hai.

---

## Pehli baar (sirf ek baar, ~5 min)

Is folder me terminal kholo (folder me right-click -> "Open in Terminal").
Prompt ke aakhir me **`arivihan-renderer>`** dikhna chahiye.

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
npm install
npx playwright install chromium
```

---

## Video banao

### Pehle ek segment test karo (~35 sec)
```powershell
node full.mjs 8
```
`out/full-video.mp4` banegi — 10 second, ~1 MB. Kisi bhi player me chal jayegi.
Dekh lo sab theek hai.

### Phir poori video (~7 min)
```powershell
npm run full
```
`out/full-video.mp4` — 110 second, ~8 MB. **Yahi editor me daalni hai.**

Aakhir me ye line aani chahiye:
```
All text verified against the spec.
```
Ye line = har shabd aur label jo spec me tha, screen par verify ho chuka hai.

---

## Editor me

Project **1080x1920**. Sirf 2 track:

| Track | Kya |
|---|---|
| 1 (neeche) | `out/full-video.mp4` |
| 2 (upar)   | HeyGen avatar, green screen key karke, neeche wale aadhe me |

Bas. Export.

---

## HeyGen

`spec/segments.json` kholo. Har segment me `"voiceover"` line hai — wahi 11 lines
bolwao, green screen par. Segment 1 ki line 0 sec par shuru, segment 2 ki 10 sec par,
segment 3 ki 20 sec par... aise 10-10 second par.

---

## Background badalna ho

`assets/chalk-background.png` ko apni image se replace kar do (1080x1920).
Ya doosri file use karni ho:
```powershell
$env:BG="assets/meri-image.png"; npm run full
```

---

## Preview (timing check karne ke liye)

```powershell
node server.mjs
```
Chrome me: `localhost:5178/renderer/index.html`  (URL Chrome me, terminal me NAHI)
Chrome me `Ctrl` + `-` se zoom out karo.
Band karne ke liye terminal me `Ctrl+C`.

Timing badalni ho to `spec/segments.json` me `t_in` / `t_out` badlo, browser refresh.

---

## Segment map

| # | Content | Diagram |
|---|---|---|
| 1 | Hook: 4 number pakke | periodic table, d-block highlight |
| 2 | Definition: last electron d-orbital me | orbital boxes + udta electron |
| 3 | Transition elements, partially filled | wahi boxes + khaali brace |
| 4 | Char 1: metallic bonding | metal lattice + free electron sea |
| 5 | Hard, ductile, malleable + melting point | wahi lattice + slip layer |
| 6 | Conductors + char 2 ka intro | metal bar, electron flow + heat |
| 7 | Variable oxidation state | Mn ladder +2 -> +7 |
| 8 | ns aur (n-1)d energy lagbhag same | energy levels + bonding arrows |
| 9 | Recap: definition | orbital boxes |
| 10 | Recap: dono characteristics + 4 number | ladder |
| 11 | Close: screenshot lena | (answer photo yahan) |

**Seg 11 (100-110 sec):** exam-answer ki photo editor me STAGE zone par daalni hai
(y 380-850), ~3.5 sec se 10 sec tak. Text upar hi rahega, avatar neeche hi rahega.

## Layout

| Zone | y (1920 me) | Kya |
|---|---|---|
| Text | 100 - 340 | Caption hamesha TOP par. Center me kabhi nahi. |
| Diagram | 380 - 850 | Text ke NEECHE |
| Khaali | 850 - 960 | gap |
| Avatar | 960 - 1920 | Sirf avatar. Koi line nahi, kuch nahi. |

---

## Kuch atke to

| Error | Fix |
|---|---|
| `running scripts is disabled` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `Could not read package.json` | Galat folder — `cd arivihan-renderer` |
| `playwright ... without first installing dependencies` | Galat folder — `cd arivihan-renderer` |
| `ffmpeg: not found` | `winget install ffmpeg`, phir terminal restart |
| `TEXT MISMATCH` | `spec/segments.json` me typo — message bata dega. Us file ko use mat karna. |
| `http://localhost... is not recognized` | URL Chrome me daalo, terminal me nahi |

**Pehla sawal hamesha:** prompt me `arivihan-renderer>` likha hai?

---

## Purana tarika (agar kabhi zaroorat pade)

`npm run render` abhi bhi kaam karta hai — wo 11 alag `.mov` files banata hai
alpha channel ke saath. Bahut bhaari (400 MB per 10 sec) aur dheema hai.
Zaroorat sirf tab jab background har segment me alag chahiye.
Normal kaam ke liye `npm run full` hi use karo.
