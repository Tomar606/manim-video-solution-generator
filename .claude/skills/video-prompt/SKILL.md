---
name: video-prompt
description: Write battle-tested Veo/Flow video-generation prompts for educational concept reels (Class 10-12 derivations/concepts, Hinglish voiceover, 9:16 vertical, 10-sec segments, bottom-50% empty for presenter overlay). Use WHENEVER the user asks for "video prompts", "segment prompts", "Veo/Flow prompts", "animation prompts", "prompt likh do", "segments bana do", "derivation video prompts", or pastes a Hinglish teaching script/topic wanting generation-ready prompts. Also trigger on /video-prompt, /vprompt, /segments. Encodes every hard-won fix — 50% background rule (invisible middle line), double-text fix, clean pop entry, golden keyword rules, 3D render quality, equation solo moments, HIGHLIGHT rule, diagram timing sync, EXACT COUNT rules, tailored negatives — so clips come out correct first try. NEVER write these prompts from scratch without this skill; every rule exists because a real generation broke without it.
---

# Video Prompt Writer — Arivihan Concept Reels

Battle-tested prompt pack generator for AI video tools (Veo 3 / Google Flow). Har rule ek real bug se nikla hai. Rules ko "simplify" ya "shorten" karna = bug wapas aana.

**Read `references/blocks.md` before writing ANY segment** — usme har block ka LOCKED verbatim text hai. Blocks ko copy karo, sirf variables fill karo. Apni marzi se reword mat karo.

**Read `references/bug-ledger.md`** jab bhi koi rule change/remove karne ka mann ho, ya user koi nayi generation-bug report kare — usme har rule ka janm-karan likha hai.

---

## What the user gives vs what you produce

**User dega (baki sab skill sambhalti hai):**
- Hinglish teaching script (ya sirf topic — tab script bhi tum likho, teacher-style, ~20 words per 10 sec)
- Topic/class context
- Optionally: kaunse hisse me diagram, kaunsi equation
- Background image (Arivihan branded, logo included) — Gemini me upload hoti hai

**Tum doge:** ek single `.md` file — prompt pack — jisme:
1. Title + segment count (`N × 10 sec = total`)
2. Fix checklist table (top par, house style — see blocks.md §14)
3. Segment map table (`Seg | Content | Diagram ✅/❌`)
4. Tool settings line (`**Tool setting:** 1080×1920 select karna.`)
5. Har segment ka fully self-contained prompt in a ``` code block — copy → paste → generate

**Missing info par sharp questions (max 2-3, ek saath):**
- "Script final hai ya main likhoon?"
- "Equation kaunsi aur kis point par aani chahiye?"
- "Diagram me kya-kya objects chahiye?" (agar unfamiliar topic)

---

## Step 0 — Accuracy brief (subject facts, BEFORE any prompt)

Generation models draw confident wrong science: sickle cell curling the wrong
way, RBC with a nucleus, haemoglobin as one blob, DNA left-handed, mitosis with
the wrong chromosome count. Na script isko rokti hai, na style rules — kyunki ye
prompt me likha hi nahi hota. Isliye pehle facts pin karo, phir prompt likho.

Script padh kar ek short brief likho — sirf wo cheezein jo **dikhti** hain:

| Kya | Example (sickle cell) |
|---|---|
| Shape | biconcave — dono faces par dimple, bowl ya doughnut nahi, beech me hole kabhi nahi |
| Colour | RBC hamesha red (haemoglobin se) — blue kabhi nahi |
| Count | haemoglobin = 4 chains: 2 α + 2 β |
| Position | mutation β-chain ki position **6** par, N-terminus se |
| Order | pehle oxygen girta hai → phir HbS polymerise → tab shape badalta hai |
| Never | mature mammalian RBC me nucleus, frameshift, chain length change |

Brief ke end me **COMMON ERRORS TO AVOID** list — us topic ke specific galat
images.

Ye brief do jagah use hoti hai:
1. DIAGRAM SPECIFICATION (§5) me exact shape/colour/count wahan se aate hain.
2. NEGATIVE list me har "COMMON ERROR" ek explicit ban ban jata hai —
   `a red blood cell with a visible nucleus`, `a left-handed DNA helix`,
   `a sickle cell shaped like a banana with rounded ends`.

Subject-matter par sure nahi ho to user se pooch lo — galat science wali clip
regenerate karni padti hai, aur wo sabse mehnga bug hai.

**Syllabus rule:** jahan NCERT simplify karta hai, NCERT follow karo — video wahi
match kare jo bachche ko padhaya gaya hai.

**Source script ko blindly mat maano.** Faculty doc me bhi galti ho sakti hai, ya
wo technically sahi par syllabus se alag ho sakta hai. Har factual detail —
codon, number, position, naam — NCERT ke wording se cross-check karo. Mismatch
mile to NCERT jeetta hai, aur user ko batao ki source doc me kya badla:

> Real case: doc me "GAG → GTG" tha (DNA coding strand — biologically sahi).
> NCERT "GAG → GUG" chhapta hai (mRNA codon). Dono sahi hain, par exam me GUG
> aata hai. Brief ne doc ko maan liya, prompt me GTG gaya, clip galat bani.

## Step 1 — Script pass

1. **Spelling/grammar fix** karo par wording user ki rakho (e.g. `banker → bankar` type corrections). Script ka har shabd screen par jayega — word-for-word, no paraphrase.
2. **Duplicate-word scan:** har phrase me check karo koi word do baar to nahi (the `nahi nahi` bug). Agar script me legitimately repeat hai (e.g. "step by step"), us segment me EXACT COUNT line likhna zaroori hai.
3. **10-sec chunks:** ~18-22 words per segment (energetic teacher pace). Natural pause par kaato, mid-clause kabhi nahi.
4. **Phrase split:** har segment ke andar 2-3 phrases. Har phrase ≤ ~9 words, max 3 short centred lines me fit ho.

## Step 2 — Segment plan

Har segment ko classify karo (yahi blocks.md ka variant decide karta hai):

| Type | Kab | Key blocks |
|---|---|---|
| **TEXT_ONLY** | Hook, pure baat | NO DIAGRAM block |
| **DIAGRAM** | Object banate/dikhate waqt | 3D RENDER QUALITY + DIAGRAM SPEC + TIMING SYNC |
| **EQUATION_ONLY** | Formula ke steps samjhate waqt | NO DIAGRAM + EQUATION RULE + HIGHLIGHT RULE |
| **TRANSITION** | Diagram fade → equation aaye | Short 3D block + fade spec + EQUATION RULE |
| **DIAGRAM+EQUATION** | Dono saath (rare — chhota diagram) | Full 3D + EQUATION RULE, diagram ko chhota rakho |

**Equation solo principle (v9 ki sabse badi seekh):** math symbols (`ε₀`, `∮`, `Φ`, `4πr²`) model ke liye sabse mushkil hain. Jab equation ke steps chal rahe hon, diagram hatao — equation ko clean solo moment do. Ek derivation me zyada tar segments EQUATION_ONLY honge.

**Proven scale:** 13 segments × 10 sec ek concept/derivation ke liye sweet spot hai (RBC reference). 21+ segments = text-load zyada, quality girti hai. Lambi script ho to script tight karne ka suggest karo.

**Continuity chain:** har segment ka `SCREEN AT START` pichle segment ke end-state se EXACTLY match kare. Segment likhne se pehle likh lo: "Seg N ends with: [objects on screen]". Carry-over objects "already present at the very first frame and does not fade in again".

## Step 3 — Build each segment

Blocks ko **is exact order** me assemble karo (order bhi tested hai):

1. `VIDEO PROMPT — SEGMENT X OF N` header + Duration line
2. VOICEOVER NARRATION (exact script)
3. AUDIO
4. FRAME LAYOUT (variant A/B/C/D — invisible middle line language)
5. Diagram-side blocks: NO DIAGRAM **ya** 3D RENDER QUALITY + DIAGRAM SPECIFICATION + DIAGRAM TIMING SYNC
6. EQUATION RULE + HIGHLIGHT RULE (equation segments only)
7. TEXT CORRECTNESS RULES (+ EXACT COUNT lines jahan zaroorat)
8. TEXT STYLE RULE
9. TEXT ENTRY AND EXIT RULE
10. SCRIPT TEXT ON SCREEN
11. STRICT FRAME LAYOUT
12. VISUAL STYLE (variant)
13. BACKGROUND — background image upload kar rahe ho to §15 (uploaded version).
    Sirf tab §12 use karo jab koi background attach nahi ho raha.
14. SCREEN AT START
15. ANIMATION TIMELINE
16. MANDATORY ON-SCREEN TEXT (numbered list, har line exactly once)
17. NEGATIVE (base variant + segment-specific bans)

### Timeline patterns (0.2s gap baked in)

- 2 phrases: `0.0–4.8 s` / `5.0–10.0 s`
- 3 phrases: `0.0–3.3 s` / `3.5–6.6 s` / `6.8–10.0 s`
- Object entries: phrase ke start ke 0.4–1.5 s baad, **exactly jab uska naam screen par ho**. Timeline me likho: "At X s, exactly as the [object] is named on screen, ..."
- Labels: phrase khatam hone ke baad ya last 2-3 sec me pop karo, "holds to the end".
- v9 pattern bhi valid: last 2-3 sec me NO script phrase, sirf labels pop ho (breathing room).

### Golden keyword decision (har phrase ke liye)

```
Phrase me math symbol / standalone letter (E, dA, +q, r) / koi word do baar?
  → YES: poora phrase UNIFORM bold white. NO golden word. (warna word toot-ta hai / duplicate hota hai)
  → NO:  exactly EK golden keyword — single simple word, no apostrophe, no hyphen,
         no math. ("Gauss's" ❌ → "Law" ✅. "step-by-step" ❌ → "derivation" ✅)
```

### EXACT COUNT rule (kab likhna)

Jab bhi koi word/symbol clip me ek se zyada jagah aata hai (phrase + label, ya phrase + equation) — TEXT CORRECTNESS me exact count line do:
> `EXACT COUNT: the letter "E" appears exactly TWICE in total in this clip — once inside the first phrase and once inside the equation. Nowhere else, in any size, at any moment.`

### NEGATIVE tailoring

Base list (blocks.md §13) + har segment ke specific bans:
- Time-locks: `the sphere appearing before 2.5 seconds`, `the label appearing before 7.0 seconds`
- Count-locks: `a second label plate`, `a third "Closed Surface"`, `two copies of the equation`
- Type-specific: equation segs me `a floating letter E anywhere outside the equation`; diagram segs me `a flat two dimensional circle instead of a three dimensional sphere`

## Step 4 — QC (har segment par, output se pehle)

`references/bug-ledger.md` ke checklist se verify karo. Non-negotiables:
- [ ] Koi %, pixel number, zone/band naam kahin bhi "visible text" instruction ke roop me nahi
- [ ] Har object ki entry-time par uska naam phrase me on-screen hai
- [ ] Har phrase ka golden/uniform decision sahi hai
- [ ] MANDATORY list me har on-screen text hai (labels + equation included), counts sahi
- [ ] SCREEN AT START = pichle segment ka end-state
- [ ] Equation one line, HIGHLIGHT rule present, koi symbol equation se bahar copy nahi hota
- [ ] Background me "no bokeh, no particles" wala version hai (bokeh wala OLD hai)
- [ ] NEGATIVE me segment-specific time/count locks hain
- [ ] Accuracy brief ka har COMMON ERROR NEGATIVE me explicit ban bana hai
- [ ] Uploaded background use ho raha hai to §15 block hai (§12 nahi), aur
      "regenerated background" wale negatives maujood hain
- [ ] Prompt me kahin bhi "logo", "watermark", "badge", "wordmark" shabd NAHI hai
      (base negative list ka `watermark` exception hai) — dekho blocks.md §16 (REMOVED)
- [ ] Diagram ka shape/colour/count accuracy brief se match karta hai

## Step 5 — Output

Poora pack ek `.md` file me `/mnt/user-data/outputs/` me save karo (naam: `<topic>-<N>-segments-prompts.md`), `present_files` se do. Chat me sirf: segment map + koi assumptions + "pehle Segment 1 test karo, phir baaki generate karo" wali line.

**Naya bug aaye to:** user se broken output ka description/OCR lo → root cause identify karo → fix ko RULE bana ke saare affected blocks me daalo → bug-ledger me entry add karo → pack regenerate karo. Yahi loop in prompts ko yahan tak laya hai.
