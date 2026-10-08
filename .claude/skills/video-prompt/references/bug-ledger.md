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

---

## Daniell cell test (Aug 2026) — PYQ/Veo track, zinc electrode beat

Pehla real generation us track ka jahan clip me **ek bhi character nahi** aa
sakta (labels alag se typeset hote hain). Science bilkul sahi aayi — liquid
colourless, pitting sirf submerged hisse par, koi bubble nahi, koi text nahi.
Layout poora fail hua, aur dono bugs ek hi jagah se nikle.

**BUG: prompt me percentage likha tha, us track me jahan text allowed hi nahi.**
PYQ contract literally bhej raha tha "between 26% and 50% of the frame height"
aur "the top 26% of the frame stays empty". Ye ledger ki entry #1 ki exact
repeat hai (`12-30%`, `Band D` screen par chhap gaya tha) — aur yahan to ek
letter bhi clip ko unusable kar deta hai.
→ RULE: layout ke numbers sirf code me rahenge (`veo_prompts.LAYOUT`), prompt me
  kabhi nahi. Prompt do invisible guide lines ki baat karta hai aur subject unke
  BEECH me baithta hai. `audit()` ab percentage / pixel count / zone name wale
  prompt ko REFUSE karta hai.

**BUG: rod poore frame ki height me chala gaya, dono edges se kat gaya, aur
clip ke dauraan bada bhi ho gaya.**
Prompt ne bataya tha ki subject KAHAN baithta hai, par ye kabhi nahi kaha ki
poora object frame ke andar hona chahiye. Jis cheez ka ek lamba axis hai — rod,
column, tube, strip — usko horizontal band se bandhna tab tak kaam nahi karta
jab tak uske **sire (ends)** define na karo. Bound na mile to model rod ko dono
taraf frame ke bahar nikal deta hai aur band ko ignore kar deta hai.
→ RULE: "THE WHOLE SUBJECT IS INSIDE THE PICTURE" block — dono ends dikhein,
  upar aur neeche clear background, kisi bhi edge se cut nahi, aur poori height
  span nahi. Lambi cheez ko **chhota karke poora dikhao**: "a small complete
  object is correct; a large one running out of frame is not."
→ NEGATIVE additions: `the subject running off the top edge, running off the
  bottom edge, being cut off by any edge of the picture, spanning the full
  height of the frame`.
→ Same-size clause bhi add hua: "exactly the same size in the last frame as in
  the first" — kyunki locked-camera likhne ke bawajood scale badla.

**BUG (authoring, model ka nahi): brief ne hi crop invite kiya.**
Brief me likha tha "A close view of the zinc rod…". "Close view" ka matlab hi
cropped subject hai, jo band layout se seedha ladta hai.
→ Sabak: band layout wale beat ka brief COMPLETE aur COMPACT subject maange —
  "the complete rod, shown whole and small, both ends visible" — "close view"
  kabhi nahi.

**Sabak (general):** subject ki SHAPE aur layout ki shape ka match dekho. Ek
horizontal band me vertical cheez daalna model ke liye contradiction hai; wo use
apne tareeke se resolve karega, aur uska tareeka hamesha frame bharna hoga.

**BUG: clip poori tarah galat background par bani — plate discard ho gayi.**
Plate dark navy hai chemistry line-art ke saath; clip plain white vignette par
aayi. Model ki galti NAHI thi: image sirf project library me upload hui thi, us
generation se ATTACH kabhi hui hi nahi. Flow me upload karna aur prompt se
reference karna do alag kaam hain — prompt bar ke asset picker me tile click
karne se attach hota hai, aur uska proof prompt bar par CHIP hai.
→ RULE: upload ke baad hamesha attach karo, aur chip verify karo. Bina chip ke
  submit karna matlab bina reference ke generate karna.
→ Sabak: "upload ho gaya" success signal nahi hai. §15 ka poora mechanism doosre
  step par tika hai, aur wo step Python side se dikhta hi nahi.

**BUG: frame review ne us galat background ko pass kar diya.**
Check B poochta tha "background pehle aur aakhri frame me same hai kya" — ek
invented background apne aap se perfectly consistent hota hai, to wo pass ho
gaya. Review ke paas koi reference hi nahi tha ki background hona kya chahiye
tha.
→ RULE: plate ko review me IMAGE 1 ki tarah bhejo aur check B0 usse compare
  kare. Alag background = seedha `fail`, sabse pehle.
→ Sabak: gate tabhi kaam karta hai jab uske paas sahi ka reference ho; "consistent"
  aur "correct" ek cheez nahi hai.

**BUG: plate attach hone ke baad bhi clip apne hi background par bani.**
Frames mode active tha, chip bhi prompt bar par tha — phir bhi background white.
Wajah prompt me thi: brief ne "a zinc rod in a shallow pool of solution" maanga.
Pool poore lower frame ko bhar deta hai, yaani plate ko REPLACE kar deta hai.
Koi bhi image-conditioning us prompt se nahi jeet sakti jo screen bharne wali
alag picture describe kar raha ho.
→ RULE: jo cheez clip me hai wo plate ke UPAR baithi ek COMPACT object honi
  chahiye — plate uske charon taraf dikhta rahe. Koi floor, wall, tabletop,
  horizon, room ya liquid ka phaila hua expanse nahi. Contract me ye positively
  likha hai aur NEGATIVE me enumerate kiya hai.
→ Sabak: §15 sirf "background describe mat karo" nahi hai. Subject ka apna
  environment bhi background hi hota hai, aur wahi plate ko kha jata hai.

**BUG: parts sab sahi, shape galat — ovule ke saare hisse aaye par structure hi galat tha.**
Prompt me stalk, do coats, opening, tissue aur sac — sab list kiye the, aur sab
aaye bhi. Par question ANATROPOUS bijand maangta hai, jiski poori pehchaan yahi
hai ki body 180° ulti hoti hai aur micropyle ghoomkar funicle ke BAGAL me aa jata
hai. Wo ek baat likhi hi nahi thi, to model ne generic seedha ovule bana diya —
har part sahi, diagram galat.
→ RULE: brief me pehle us cheez ka DEFINING SHAPE likho, uske baad parts. "Kya-kya
  hai" se pehle "dikhta kaisa hai". Jis feature ke liye diagram poocha gaya hai,
  wahi sabse pehli line honi chahiye.
→ Sabak: parts ki list complete hone se structure sahi nahi ho jata.

**BUG: "X ke andar Y" ko model ne ek hi cheez bana diya.**
"nucellus ke andar embryo sac" maanga tha; mila ek hi oval jo poora interior bhar
raha tha. Nesting apne aap nahi aati — do alag cheezein tabhi banti hain jab
farq explicitly likha ho.
→ RULE: nested structure ke liye teen baatein likho — andar wali cheez OUTER se
  clearly CHHOTI hai, uske charon taraf outer ka rim DIKHTA hai, aur andar wali
  ka apna andar khaali hai (agar baad me usme kuch daalna hai).
→ Sabak: "inside" ek relationship hai, aur model relationship se zyada shape
  samajhta hai. Size aur margin likho, "inside" ke bharose mat raho.

**BUG (mera, model ka nahi): accuracy brief hi galat thi.**
Maine check likha tha "micropyle stalk ke ULTE sire par" — wo ORTHOTROPOUS ovule
ke liye sahi hai, anatropous ke liye nahi. Agar ye pakda na jata to dus ke dus
clips confidently galat bante, aur frame review bhi pass kar deta — kyunki review
brief ke against grade hota hai.
→ RULE: brief ka har structural claim source (script/NCERT) se cross-check karo,
  apni yaad se nahi. Ye wahi GAG/GTG wala sabak hai: brief ka kaam sirf model ko
  batana nahi, source ko check karna bhi hai.
→ Isiliye MASTER pehle banta hai aur alag se verify hota hai. Ek still par galti
  pakadna sasta hai; dus clips ke baad pakadna mehnga.

**BUG: colour theek karne gaye, shape toot gaya.**
v4 me structure bilkul sahi tha par chaaron parts ek jaise green the. v5 me colour
ke liye poora paragraph joda — chaaron ke naam le kar (deep green, orange-brown,
cream, blue). Colour perfect aa gaya, par ovule ab symmetric, seedha, sepal-jaisi
pattiyon ke saath ek phool ki kali ban gaya. Anatropous inversion gayab.
→ RULE: emphasis zero-sum hai. Prompt me kisi ek cheez par zor badhaane se baaki
  instructions ka weight GIRTA hai. Ek waqt me ek axis theek karo, aur structural
  line ko chhota mat karo — usse chhoti si edit se sudharo, naya paragraph jodkar
  nahi.
→ Sabak: jo already sahi aa raha hai use "safe" mat maano. Har regeneration me wo
  dobara jeeta jaata hai, aur lamba prompt usko haraa deta hai.

**Kaam ki baat: abstract constraint vs named value.**
"chaar alag colours" -> chaar shades of green mile (technically alag, padhne me
ek jaise). "deep leaf green, warm orange-brown, pale cream, clear medium blue" ->
bilkul theek. Wahi pattern jo nesting me tha: "inside" kaam nahi karta, "smaller
+ rim visible + empty" karta hai.
→ RULE: relationship ya quality maangne ke bajaye VALUE do. Model quality ko
  loosely satisfy karta hai, value ko exactly.

**CORRECTION: "reference image lagane se shape sahi aa gaya" — ye conclusion ek
hi sample par tha aur galat nikla.**
Reference ke saath teen attempts hue: v4 sahi, v5 aur v6 dono me shape wapas
symmetric bud ban gaya. Yaani 1/3, reliable nahi. v4 shayad luck tha.
→ Asli wajah image quality lagti hai: reference ek grainy, stippled photocopy hai
  jisme ovule ka outline print noise se ladta hai aur funicle ka upar se jaana
  saaf dikhta hi nahi. Model usse "ovule jaisa kuch" nikaal leta hai par exact
  geometry nahi — aur phir apne prior par chala jaata hai.
→ RULE: reference tabhi kaam karta hai jab wo PADHNE LAYAK ho. Scan attach karne
  se pehle khud dekho: jo feature aap chahte ho, kya wo image me saaf hai? Nahi
  to reference se madad nahi milegi, sirf ek aur variable jud jayega.
→ Sabak (mera): ek sample se "validated" mat bolo. Teen attempt ke baad hi pata
  chala ki v4 outlier tha, aur tab tak main user ko bata chuka tha ki approach
  kaam kar gayi.

**BUG: green screen par plant diagram — embryo sac ka rang background jaisa hi
aa gaya, aur key ne wahin ched kar diya.**
Ovule ka bhrun kosh rgb(35,189,37) aaya, background rgb(33,190,37). Key ko dono
me farq nahi dikha, to diagram ke SABSE ZAROORI hisse ki jagah transparent hole
ban gaya. Funicle bhi aadha gayab. Prompt me "nothing in the drawing is green"
likha tha — model ne phir bhi green use kiya, kyunki paudha green HOTA hai.
→ RULE: chroma field aisa chuno jo subject me ho hi na sakta. Botany ke liye
  BLUE (#0047BB), baaki (animal, molecular) ke liye green. `veo_prompts.CHROMA`
  me dono hain.
→ Blue par wahi ovule dobara banaya: har hissa — brown sac, yellow nucellus,
  orange coat, GREEN flap tak — key ke baad opaque rehta hai. Green flap green
  screen par gayab ho jaata.
→ Sabak: subject ke khilaf rule likhne se accha hai aisa setup chuno jisme wo
  rule zaroori hi na ho. "Green mat banao" har clip par ladta hai; blue field
  par ye sawal hi khatam.
→ Aur ye bug SABSE KHATARNAK type ka hai: clip dekhne me perfect lagti hai,
  ched sirf compositing ke BAAD dikhta hai.

**BUG: batch me clips galat question ke naam se save ho gaye.**
14 clips ek ke baad ek generate kiye. `gen()` har clip ke liye "jo agla naya
video key aaye" utha leta tha. Par Flow generations ko QUEUE karta hai aur wo
OUT OF ORDER poori hoti hain — to ek dheemi clip agle clip ke poll ke dauraan
aa girti hai aur uske naam se save ho jaati hai. Teen clips pakde gaye kyunki
unka background rang filename se nahi milta tha (blue clip green naam ke saath).
Jo do clips ek hi field par thay, wo swap hue hon to ye test unhe pakad bhi nahi
sakta.
→ RULE: submit karte waqt ek pehchaan bhejo aur wapas aane par MILAO. Sirf
  "naya key aa gaya" kaafi nahi hai. Behtar: ek waqt me ek hi generation chalne
  do (submit ke baad uska video aane tak agla submit mat karo) — jo hum kar rahe
  the — PAR uske saath ye bhi check karo ki jo aaya wo issi prompt ka hai.
  Chroma field ka rang ek sasta fingerprint hai jab do lagataar clips ke field
  alag hon.
→ Sabak: yahi galti teesri baar alag roop me aayi — placeholder wali, upload wali,
  aur ab queue wali. Teeno ka core ek hi hai: "jo agli cheez dikhi wo meri hai"
  maan lena. Flow me kuch bhi order me nahi aata.


## Correction jo brief file me nahi gayi, wo exist hi nahi karti (Aug 2026)

`bio_BIO-C1-LA-01_plan.md` me ek CORRECTION section likha tha: ovule anatropous
hai, yaani micropyle funicle ke BAGAL me, uske ulte sire par nahi. Wo likha gaya
aur `bio_animations.py` / `bio_ovule_clips.py` me kabhi nahi pahuncha — jinhe
generator asal me padhta hai. Dono me abhi bhi likha tha "gap stalk se door wale
sire par". Veo ne brief ko theek-theek follow karke orthotropous ovule bana diya,
aur frame review ne use PASS kar diya — kyunki review clip ko brief ke against
grade karta hai.

→ Yahi galti is project me teesri baar: GAG/GTG, accuracy brief, ab yeh.
→ Sabak: **pehle wo file theek karo jo generator padhta hai, prose baad me.**
  Sirf prose kabhi nahi. Sasta check: corrected term ka grep saari brief files par.

## Veo verb banata hai, number nahi (Aug 2026)

14 biology clips, har ek apne hi checks ke against graded: 7 pass, 3 borderline,
4 fail. Aur har fail ek discrete quantity ya topology par hua jo khud hi answer
tha. 9:3:3:1 nikla 9:4:4:4. Teen antipodal nikle do. Arrow ki direction ulti.
Trophic tiers upar-neeche. Base pairs kisi bhi base ke saath jud gaye.

Jo saare pass hue, unme se kisi ne count nahi maanga — sirf manner, action ya
habitat maanga.

→ Rule: subject par mat route karo, MARK par karo. Agar mark ko count, ratio,
  order ya direction me likha ja sakta hai — wo Manim ka hai. Agar mark "yeh hota
  kaise hai dikhao" hai — wo Veo ka hai.
→ Jahan subject organic ho par mark number ho, wahan hybrid sahi hai: body Veo se
  chroma par, counts/arrows/labels Manim se upar composite.

## Chroma field ke against har named colour check karo (Aug 2026)

C5-LA-03 ka base-pairing fix likhte waqt maine rung ke do legal pair banaye:
red-blue aur **yellow-GREEN** — aur clip GREEN screen par generate ho rahi thi.
Agar model maan bhi leta, to har yellow-green rung ka aadha hissa key out hoke
chhed ban jaata.

→ Yeh wahi bug hai jo green embryo sac ne green field par diya tha. Dobara aaya,
  aur is baar ek DUSRE bug ka fix likhte waqt aaya.
→ Rule: prompt bhejne se pehle prompt me likhe HAR colour ko chroma field ke
  against check karo. Yeh mechanical check hai, yaad rakhne wali baat nahi.

## Ek revision me ek hi nayi demand (Aug 2026)

C2-LA-02 me ek saath do cheezein maangi: ovary add karo, aur drawing ko frame ke
andar rakho. Ovary aa gayi, framing pehle se kharab ho gayi — drawing bada hoke
dono edges par kat gaya.

Wahi clip, sirf framing badalke, aur abstract ke bajaye concrete units me
("picture width ka beech wala TIHAAI") — pass ho gayi, ovary bhi bani rahi.

→ Emphasis zero-sum hai. Do nayi demand = ek hi land karegi.
→ Rule: **ek revision me ek hi nayi demand, aur usse aise units me likho jo model
  naap sake** ("middle third of the picture width"), na ki feel me ("a wide band").

## Khaali jagah ko kabhi describe mat karo — SUBJECT ko describe karo (Sep 2026)

Biology split-screen ke liye ek 4:3 panel chahiye tha, par Flow ki **video**
generation sirf 16:9 aur 9:16 deti hai (image generation 4:3 deti hai — dono
row alag hain, aur yeh maine DOM naap kar confirm kiya). To plan yeh tha: 16:9
generate karo, subject ko beech me rakho, phir centre se 4:3 crop kar lo.

Prompt me maine likha: *"a wide band of empty dark background along the left
edge and an equally wide band along the right edge"*.

Veo ne wo bands **literally draw kar diye** — dono taraf hard BLACK PILLARBOX
bars. Asli picture ek square (720x720) ban gaya jo 1280x720 frame ke beech me
inset tha. Upar se "camera pushes in" ne us inset picture ko poore frame tak
zoom kiya, to framing clip bhar badalti rahi: shuru me mote bars, aakhir me
full frame aur specimen top-bottom se kata hua.

→ Yeh wahi logo-rule wala parivaar hai: kisi cheez ka naam lena use draw karne
  ka signal hai. "Empty band" bhi ek cheez hai. Aur ledger ki pichli entry ne
  theek yahi phrase — "a wide band" — galat unit bataya tha; main phir bhi usme
  gira.
→ Rule: **framing kabhi khaali jagah se mat batao. Subject ke aakaar aur jagah
  se batao.** "the specimen stands upright at the centre, taller than it is
  wide, its height reaching most of the way from top to bottom" — isse subject
  apne aap frame ke beech wale hisse me aa jaata hai, aur koi band draw nahi
  hoti.
→ Rule: **jo clip crop hone wali hai usme camera push-in mat maango.** Push-in
  framing ko clip ke दौरान badalta hai, to ek hi crop window shuru me sahi aur
  aakhir me galat hoti hai. Camera lock karo; motion subject ke andar rakho.
→ NEGATIVE me ab yeh explicit hain: `black bars down the sides of the picture,
  a pillarboxed picture, a smaller picture inset inside the frame, a picture
  that grows or expands to fill the frame during the clip, a camera push in,
  a framing that changes during the clip`.
