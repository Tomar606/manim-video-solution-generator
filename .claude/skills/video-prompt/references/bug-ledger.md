# BUG LEDGER — har rule ka janm-karan

Har rule ek real broken generation se aaya hai. Rule remove/soften karne se pehle yahan check karo kaunsa bug wapas aayega. Naya bug fix karo to yahan entry ADD karo (date + observed output + root cause + rule).

## Fix history (v1 → FINAL)

| # | Observed bug (real output) | Root cause | Rule that fixed it |
|---|---|---|---|
| 1 | `12-30%`, `Band D` screen par likha aa gaya | Layout instructions me numbers/percentages/zone names the — model ne unhe visible text bana diya | FRAME LAYOUT me koi number nahi; "invisible middle line" language; NEGATIVE me `any percentage sign, any zone name, any band name...` |
| 2 | Middle me visible line/band render hui | "50% line" ko model ne draw kar diya | "The invisible middle line is a composition guide only. It is NEVER drawn..." + `no split, no seam` background clause |
| 3 | Bottom half me equation ghus gayi (`my 1 ATE q r2` @9.5s) | Equation stack lamba tha, middle cross kar gaya | "lowest element stops with a clear visible gap above the invisible middle line; if it does not fit, make it smaller" + equation ONE line only |
| 4 | Double text — same sentence ki do copies | Crossfade transitions + "60% opacity faded carry-over line" wali instruction | 0.2s gap, no crossfade; faded/ghost lines ka concept hi hata diya; NEGATIVE me saare double-text variants |
| 5 | `Saabs: pehle +g charse echero tarof r radaxie=` — garbled morphing text | Letter-by-letter / morph transitions | Clean POP entry (0.15s fade+scale), "FULLY SHARP FROM THE VERY FIRST VISIBLE FRAME", no morph/typewriter/scramble |
| 6 | Random `q` aur `ATE,` floating labels | "LABELS: none" likha tha par model ne khud labels invent kiye | "IF LABELS says none — absolutely NO plate, NO letter... Never invent a label" + MANDATORY list = exhaustive |
| 7 | Golden keyword duplicate ho ke alag line me chhap gaya / word toota | Keyword multi-word tha (`Gauss's Law`), apostrophe/hyphen wala (`step-by-step`), ya math phrase me tha | Keyword = single simple word, no apostrophe, no hyphen; math/standalone-letter/repeated-word phrase = fully UNIFORM white |
| 8 | `nahi nahi` — word stutter | Model words repeat karta hai jab count lock nahi hota | "NEVER REPEAT A WORD INSIDE A PHRASE" + EXACT COUNT lines |
| 9 | `E` / `dA` phrase me bhi, equation me bhi — extra floating copies bani | Symbol do jagah likha tha, model ne teesri copy bana di | EXACT COUNT ("appears exactly TWICE — once in phrase, once in equation. Nowhere else") + HIGHLIGHT RULE (recolor in place, never copy out) |
| 10 | Flat 2D circle, sab arrows same length | 3D language absent thi | 3D RENDER QUALITY block (camera, ellipses, depth, foreshortening, slow turn) |
| 11 | Diagram phrase se pehle hi aa gaya | Entry time voiceover se sync nahi thi | DIAGRAM TIMING SYNC — "at the exact moment its name is visible on screen, never a frame before" + NEGATIVE time-locks |
| 12 | Stray `°` `©` marks + charge "jal rahi thi" (fire) | Background me bokeh/particles + glowing charge ko model ne fire samjha | Background = "completely flat and clean, no bokeh..."; charge spec me "NOT on fire, never flickers, flares, burns"; VISUAL STYLE me NO fire block |
| 13 | Teacher/person khud generate ho gaya | Layout me explicitly ban nahi tha | Pehli layout line: "TEXT AND GRAPHICS ANIMATION ONLY. NO person, NO teacher..." |
| 14 | Math steps me symbols garble hue | Equation + diagram + text sab saath — overload | EQUATION SOLO MOMENT principle: equation segments me NO diagram; equation bada, akela, one line |
| 15 | Output 720×1280 aaya | Tool default | Pack header me: "**Tool setting:** 1080×1920 select karna." |
| 16 | 21 clips me consistency toot rahi thi | Zyada segments, har clip me style drift | 13-segment RBC-proven structure; BACKGROUND/STYLE blocks har segment me word-for-word identical |

## RBC reference standard (proven benchmark)

RBC (biology) video 13 segments me clean nikla tha. Uski seekh:
1. Golden keyword tabhi kaam karta hai jab single clean word ho (`oxygen`, `HBB` chale; `Gauss's` faila)
2. Label style jo hamesha sahi render hota hai: **white rounded plate + dark bold text + short thin white leader line**
3. RBC me koi math nahi tha isliye clean tha → math ko isolate karna hi solution hai
4. Har clip ka text-load RBC jitna halka rakho (~2 phrases + max 2 labels)

## QC checklist (har segment, output se pehle)

**Layout**
- [ ] FRAME LAYOUT ka sahi variant (A/B/C/D); koi number/percent/band-name visible-text ban ke nahi aa sakta
- [ ] NEGATIVE me middle-line + bottom-half bans hain

**Text**
- [ ] Phrases: 2-3, har ek ≤ ~9 words, ≤ 3 centred lines
- [ ] Har phrase ka style decision: math symbol / standalone letter / repeated word → UNIFORM; warna exactly 1 golden keyword (single word, no apostrophe/hyphen)
- [ ] Duplicate-word scan pass; deliberate repeats ke liye EXACT COUNT
- [ ] Har cross-appearing symbol (phrase+label / phrase+equation) ke liye EXACT COUNT line
- [ ] POP entry rule present; equation segs me "or mathematical symbols" added

**Diagram / Equation**
- [ ] Sahi block-set: NO DIAGRAM ya (3D QUALITY + SPEC + SYNC) ya (EQUATION + HIGHLIGHT)
- [ ] Har object ki entry time = uska naam on-screen hone ka time; timeline me "exactly as the X is named on screen" likha hai
- [ ] Labels: white-plate style, count declared, "LABELS: none" jahan koi nahi
- [ ] Equation: ONE line, flat overlay, never moves; highlight = recolor in place; pichla highlight "returns to white"

**Continuity**
- [ ] SCREEN AT START = pichle segment ka exact end-state; carry-over objects "do not fade in again"
- [ ] BACKGROUND block har segment me word-for-word same (no-bokeh version)

**Completeness**
- [ ] MANDATORY list me har on-screen string (phrases + labels + equation), numbered, "exactly ONCE"
- [ ] NEGATIVE = universal core + type add-ons + is segment ke time-locks & count-locks
- [ ] Timeline timings 0.2s gaps ke saath; 10.0s par khatam

---

## Sickle cell test (Aug 2026) — 4 bugs from one generation

**BUG: unwanted voiceover + auto-captions.**
Clip me Veo ka apna voiceover aaya, aur uske saath burnt-in captions bhi.
Workflow badal gaya hai — ab audio HeyGen avatar se aati hai, isliye Veo ka
voiceover duplicate hai aur captions unwanted.
→ RULE: §17 SILENT CLIP. VOICEOVER + AUDIO blocks hatao, silent block lagao,
  aur auto-caption ke negatives daalo.

**BUG: animation 50% se neeche chala gaya.**
§2 FRAME LAYOUT hone ke bawajood diagram invisible middle line cross kar gaya —
presenter ki jagah kha gaya.
→ RULE: §18 SIZE AND POSITION CHECK. Diagram pehle scale hota hai taaki poora
  upper half me fit ho, aur clip ke dauraan kabhi grow/drift na kare.
→ SHAK: anchor frame landscape full-bleed tha ("poster" layout). Ho sakta hai
  frame ne "poora frame bharo" ka signal diya ho. Test: wahi segment portrait
  top-half composed frame ke saath (FRAME_LAYOUT=top_half).

**BUG: highlight sahi element par, change galat element par.**
8 beads me 6th par ring sahi aayi, par colour kisi doosre bead ka badla.
→ RULE: §19 SAME ELEMENT RULE — highlight aur change ek hi element par, number
  literal likho, aur padosi elements ko negative me naam se bando.

**Sabak:** jab bhi ek element par do actions hain, unhe explicitly bandhna padta
hai — model unhe alag elements par baant deta hai.

**BUG: sahi codon, galat form — GAG → GTG instead of GAG → GUG.**
Clip me GTG dikha. Model ki galti nahi thi: source doc me GTG likha tha aur
accuracy brief ne usi ko maan liya. GTG = DNA coding strand (biologically sahi),
GUG = mRNA codon (NCERT jo chhapta hai, aur exam me yahi aata hai).
→ RULE: Step 0 me har factual detail syllabus se cross-check hogi. Source doc
  authority nahi hai — NCERT hai. Mismatch par NCERT jeetta hai aur user ko
  batana hai.
→ Sabak: accuracy brief ka kaam sirf "model ko batana" nahi, "source ko check
  karna" bhi hai. Warna brief galti ko authority de deti hai.

**BUG: dono top corners me random logos aa gaye.**
Maine §16 "LOGO SAFE AREA" block add kiya tha — usme "logo" shabd 5 baar tha,
prompt ke positive section me, corners khaali rakhne ke liye. Model ne ulta hi
kiya: dono corners me logo bana diya.
→ RULE: §16 hata diya. Prompt me logo/watermark/badge/wordmark kabhi mat likho,
  mana karne ke liye bhi nahi. Generation me logo ka koi zikr nahi; patch editing
  me lagta hai.
→ Sabak (general): kisi cheez ka naam positive instructions me likhna — chahe
  "mat banao" ke saath — usko banane ka signal hai. Jo nahi chahiye uska naam
  sirf NEGATIVE list me aaye, aur wahan bhi kam se kam.
