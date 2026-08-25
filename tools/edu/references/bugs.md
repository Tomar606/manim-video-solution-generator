# Bug ledger

Har rule ek real failure se aaya hai. Rule hatane se pehle ye padho.

| # | Kya toota | Asli wajah | Fix |
|---|---|---|---|
| 1 | `node server.mjs` chupchaap band ho jata tha, Windows par | `import.meta.url === \`file://${process.argv[1]}\`` Windows ke `C:\...` backslash path se kabhi match nahi karta, isliye "server start karo" wala block chalta hi nahi tha | `fileURLToPath` + `path.resolve` se compare karo. `server.mjs` me fix hai. |
| 2 | Browser me `not found: renderer/index.html` | `new URL(import.meta.url).pathname` Windows par galat root deta hai | Bug 1 ka hi fix isko bhi theek karta hai |
| 3 | Seg par jhoota `TEXT MISMATCH`, jabki screen par text sahi tha | Engine `d-block`, `(n-1)d` ke hyphen ko U+2011 non-breaking me badalta hai; audit purana `-` dhoondh raha tha | Audit me dono side normalise: `s.replace(/\u2011/g,'-')`. `render.mjs` aur `full.mjs` dono me hai. |
| 4 | Oxidation ladder ke rungs invisible | Horizontal line ka bounding box zero-height hota hai; uspar `objectBoundingBox` gradient stroke render hi nahi hota | Straight lines par hamesha solid stroke |
| 5 | `d-orbital` line break par toot jata tha | normal hyphen par browser wrap karta hai | Engine har `\\w-\\w` ko U+2011 me badalta hai (bug 3 isi ka side effect tha) |
| 6 | 10 sec ki file 400 MB, poori video 4.4 GB, render 25 min | ProRes 4444 + alpha; PNG frames disk par likhe ja rahe the | `full.mjs`: background bake karo → alpha ki zaroorat khatam → H.264, JPEG frames seedha ffmpeg pipe me. 110 sec = 7.9 MB, ~6 min. |
| 7 | Text screen ke beech me aa raha tha, diagram ke saath takra raha tha | Caption `align-items:center` tha aur stage caption ke upar tha | Caption `align-items:flex-start`, `top:0`, aur zones flip: caption 100–340, stage 380–850 |
| 8 | Naye SVG bahut patle/chhote nikle, phone par dikhte hi nahi the | 1080×470 ko laptop par dekh kar "theek" lagta hai | Stroke ≥ 6px, main bar 14–18px, circle r ≥ 14, x 150–950 aur y 70–400 bharo. **Har naya SVG render karke `view` se dekho.** |
| 9 | Label diagram ke element par chadh gaya, electron bar ke bahar nikla | Coordinates bina render kiye guess kiye the | Frame nikaal ke dekho, phir adjust karo. Validator ye nahi pakadta. |
| 10 | Validator ne har SVG par "text element" ka error diya | SVG ke comment me `<text>` rule likha tha, regex use pakad raha tha | Comment strip karke check karo: `re.sub(r'<!--.*?-->','',src,flags=re.S)` |
| 11 | Hook segment gayab tha | Script ka pehla line hook tha, use normal segment maan liya | Hook hamesha Segment 1. User ka diya hua hook verbatim use karo. |
| 12 | Avatar 3 second chup khada rehta tha | Segment me sirf 14 words the (1.4 w/s) | Har segment 18–22 words. Balance karne ke liye lines shift karo, likho mat. |
| 13 | Container me `npm run render`/`full.mjs` beech me mar jata tha | Command timeout ~300s, full render ~340s | Background me chalao + `sleep 290`, phir log padho. `nohup` bhi shell exit par mar sakta hai — subshell + `&` use karo. |
| 14 | `node full.mjs` par `Cannot find package 'playwright'` | `npm install` nahi chala tha us copy me | Naye folder me hamesha pehle `npm install` |
| 15 | Playwright browser download 403 | `cdn.playwright.dev` allowlist me nahi | Container me pehle se maujood binary use karo: `CHROME_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (number badal sakta hai, `ls /opt/pw-browsers/` karo) |
| 16 | Poora render (>150 sec video) container me beech me mar jata tha, 59% par | Ek command ka wall-clock limit hai; 5160 frames ~9 min lete hain | **Chunks me render karo:** `node full.mjs 1,2,3,4` -> `chunk-A.mp4`, phir agla chunk. Aakhir me `ffmpeg -f concat -safe 0 -i list.txt -c copy final.mp4`. Seams check kar lo (join ke 0.1s pehle/baad ka frame nikaalo). |
| 17 | Ek segment me pichle topic ka diagram bacha reh gaya | Topic badal raha tha par purane asset ke parts fade out nahi kiye the | Jab agla segment DOOSRA asset use kare, current segment ke ~6.6s par purane asset ke **saare** visible ids `fade_out` karo aur `end_state` khaali chhodo |
| 18 | Arrow bilkul nahi dikha (Gibbs ka red arrow, energy-flow ke arrows) | Element ka **ekmatra action `draw`** tha. `draw` sirf `strokeDashoffset` set karta tha, `opacity` nahi — aur non-carry items ki initial opacity 0 hoti hai, to wo hamesha invisible rahe. Saath hi `draw` sirf `<path>` par kaam karta tha, `<g>` par nahi. | Engine fix: `draw` ab opacity bhi ramp karta hai, aur `<g>` ke stroked children ko bhi dash karta hai. Spec me phir bhi `fade_in` + `draw` saath do. QA ka `ORPHAN` check isko pakadta hai. |
| 19 | Label box se bahar nikal gaya ("Chemical Energy" 415px, box 430px) | Box ki apni `id` nahi thi — QA ne poore `<g>` (780px) ko container maana, isliye overflow miss ho gaya | Har container shape ko apni `id` do. QA ka `OVERFLOW` check ab exact px me batata hai. |
| 20 | Screen par akeli dashed line 3s tak, kuch aur nahi | `baseline` 1.0s par aata tha par baaki diagram 4.4s par | Scaffolding (axis, baseline, divider) ko main content se ~1.2s pehle hi laao, zyada nahi. QA ka `LONE` check. |
| 21 | Diagram zone 3.5s tak khaali raha | Diagram build phrase 2 ke saath shuru kiya tha | Diagram har segment me **~1.5s ke andar** dikhna shuru ho. QA ka `NO_DIAGRAM` check. |
| 22 | Diagram ke neeche alag hi text tair raha tha ("4 number pakke!") | Caption jaisi line ko `label` bana diya tha, jabki wo caption me already thi | Labels sirf **diagram ke hisson ke naam** hote hain. Koi bhi poora vaakya caption me jaata hai, label me kabhi nahi. |
| 23 | Hook ke pehle hi line par diagram aa gaya | Diagram build segment ke shuru me schedule kar diya tha | Diagram tab aaye jab uska naam bole. Intro line ke waqt stage khaali sahi hai — QA lead-in 5s allow karta hai. |
| 24 | Galvanic aur Electrolytic dono ka diagram ek saath dikh raha tha | Comparison asset ke dono side ek hi segment me build kar diye the | **Ek waqt par ek topic.** A dikhao, A hatao, phir B. Ids side-prefixed rakho; QA ka `BOTH_SIDES` check pakadta hai. |
| 25 | Har doosri phrase me colon lag gaya tha | Lamba vaakya chhota karne ka aasaan rasta colon lagta hai | Natural Hinglish likho. QA ka `COLON` check. |
