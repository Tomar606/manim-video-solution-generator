# PYQ script format — MP Board Class 12 (Hindi medium)

House format for the previous-year-question videos. **The authority is
`style/samples/` — two manually verified scripts (फैराडे के नियम, संक्षारण).**
This file only writes down what they already do. When the two disagree, the
samples win.

## Structure

```
प्रश्न N — <विषय>

भाग 1 — शुरुआत 🎙️
शिक्षक:
"<hook: board, class, year, त्रैमासिक परीक्षा, promise>"

भाग 2 … भाग N-1 🎙️     ← one concept per भाग
भाग N — अंतिम भाग 🎙️    ← recap, answer card, उन्नति बैच
```

Every भाग: the `🎙️` in the heading, `शिक्षक:` on its own line, then the spoken
lines in curly quotes `“ ”`.

## From a sheet row to a script

All you get is the topic, the question and the question bank's answer. This is
what the two approved scripts actually did with theirs — derived by diffing the
sheet rows for CHE-C2-LA-01 and CHE-C2-LA-02 against the finished scripts.

### The question decides the भाग structure

Count what the question *asks for*; each one becomes its own भाग, with the hook
and the close around them.

> "संक्षारण किसे कहते हैं? इसे प्रभावित करने वाले **तीन कारकों** को लिखकर इससे
> बचाव के कोई **तीन उपाय** लिखिए।"

→ भाग 2 = definition · भाग 3 = the three factors · भाग 4 = the three measures.
Nothing more, nothing merged. When the answer contains parallel items worth
comparing (two laws, two cases), add one **recap भाग** before the close that
restates each in a single line — Faraday's भाग 4 exists for exactly that and is
in neither the question nor the answer.

### Deliver the number that was asked

The corrosion answer really only gives **two** prevention methods — barrier and
sacrificial — with electroplating buried inside the barrier one. The question
asks for three. The script promotes electroplating into its own "तीसरा—विद्युत्
प्लेटिंग". If the answer is short of the count, restructure until it isn't.

### Fill the gaps the answer leaves

That same answer opens with "संक्षारण—**प्रश्न क्रमांक 4 देखिए**" — a
cross-reference, no definition at all. The script supplies the full NCERT
definition. A sheet answer that points elsewhere, skips a step, or is wrong is
normal; write what the student needs.

### Keep the label, simplify the explanation

Every enumerated item keeps the answer's exact label and then explains it
plainly:

| answer | script |
|---|---|
| "(1) धातु की प्रकृति-अधिक क्रियाशील धातु जल्दी संक्षारित होती है।" | "पहला—**धातु की प्रकृति**, मतलब धातु जितनी अधिक क्रियाशील होगी, उस पर संक्षारण उतनी जल्दी होगा।" |

The pattern is `पहला—<answer's exact label>, मतलब <plain explanation>`. Long
lists get compressed to representatives: the answer's "ऑक्सीजन, कार्बन
डाइ-ऑक्साइड, नमी, खारापन या लवणों की उपस्थिति तथा SO₂, SO₃ आदि गैसें" becomes
"हवा, नमी और कुछ गैसों की मौजूदगी".

### Drop what earns no marks

"सन् 1832 में माइकल फैराडे ने" — gone. Discovery dates, discoverer names, image
URLs and incidental asides do not survive. LaTeX becomes clean glyphs:
`$$ W \propto Q $$` → `W ∝ Q`, `\mathrm{W}_{1}` → `W₁`.

**Derivation order is preserved exactly**, though. The answer's
`W ∝ Q` → `Q = i·t` → `W ∝ i×t` → `W = Z i t` appears in that order, with only
the lead-in phrases inserted between.

### Add the teaching the answer doesn't contain

This is the real work, and none of it comes from the sheet:

- **A memory aid** — "धातु + वायुमण्डल की गैसें + नमी = संक्षारण।" appears
  nowhere in the source.
- **An everyday example** — "और इसका सबसे आसान उदाहरण है—लोहे में जंग लगना।"
- **The mistake students actually make** — "बहुत सारे बच्चे यहीं गलती करते
  हैं। दूसरे नियम में विद्युत् की मात्रा समान रहती है…" The writer knew students
  confuse law one's W–Q relation with law two's W–E relation.
- **What the exam rewards** — "अगर परीक्षा में बिल्कुल ऐसा ही लिख दिया, तो आपके
  नंबर पक्के हैं।"

A script that only restates the answer has done none of the job. The answer is
the floor.

## Formulas are SHOWN, not spoken

This is the biggest single rule and the easiest to get wrong. **The teacher never
recites an equation.** A formula gets a lead-in phrase, then appears on screen on
its own line — outside the quotes — and the teacher then names the symbols.

```
“अब कूलम्ब में विद्युत् की मात्रा—”
Q = i × t
“जहाँ i है विद्युत् धारा की तीव्रता और t है धारा के प्रवाहित होने का समय।”
“इसलिए—”
W ∝ i × t
“और समानुपात हटाने पर—”
W = Z i t
“यहाँ Z है विद्युत्-रासायनिक तुल्यांक।”
```

Note the shape: **short lead-in → formula → what the symbols mean.** The lead-in
ends on an em-dash. A derivation becomes a rhythm of these, not a paragraph of
spoken algebra.

Never write "E बराबर, एक बटा चार पाई एप्सिलॉन नॉट, गुणा p बटा r घन" as a spoken
line. Put `E = (1/4πε₀)·p/r³` on screen and say what it means.

Use the literal label `On Screen:` before the first formula of a beat, as the
Faraday sample does.

**Individual symbols in prose are still spoken** — "यहाँ W है मुक्त पदार्थ की
मात्रा", "दोनों के बीच की दूरी है two-ell". It is whole equations that are shown.

## On-screen text: Hindi for words, notation for maths

Two different things end up on screen, and they render by different paths.

**Hindi** — titles, labels, captions, flow chains, axis names. This is the rule
for the whole channel: labelling, topic names and captions are in Hindi.

> `भीतरी नली → आसुत जल | बाहरी नली → विलयन`
> `रासायनिक ऊर्जा → विद्युत् ऊर्जा`

**Standard notation** — symbols, variables, formulae, reactions. These are
international and are never translated or transliterated.

> `ΔT_b = K_b · m`   `Zn(s) → Zn²⁺(aq) + 2e⁻`

### The rendering constraint that decides this

The bundled font (Poppins, in `assets/fonts/`) **does cover Devanagari** — all
94 glyphs, nothing missing. What it does **not** have is the notation:

| missing from Poppins | appears in |
|---|---|
| `Δ Λ α λ μ ν` | `ΔT_b`, `Λ°ₘ`, `λ°`, `α` |
| `₀₁₂₃₄ ⁰⁺⁻ ₊₋ ₐ ₘ` | `Zn²⁺`, `W₁`, `CH₃`, `Λ°ₘ` |
| `→ ⇌ ⇒ ∝ ‖` | every reaction and proportionality |

So: **Hindi words go through `Text()`** (Poppins has them), **formulae go through
`MathTex()`** (LaTeX has the Greek, subscripts and arrows natively; use
`mhchem` for reactions). Rendering a formula as `Text()` produces tofu boxes;
rendering Devanagari as `MathTex()` fails outright, because the LaTeX install has
no Devanagari support.

### Keep Devanagari out of the formula itself

A line like `ऐनोड (ऑक्सीकरण): Zn → Zn²⁺ + 2e⁻` is fine — the Hindi is a label and
the formula follows, so it splits into a `Text()` and a `MathTex()`. What breaks
is Devanagari glued *inside* a symbol:

> ✗ `E°सेल = E°कैथोड − E°ऐनोड`
> ✓ `E°_cell = E°_cathode − E°_anode` as the formula, with `सेल विद्युत्-वाहक बल`
>   as the Hindi label beside it

MP Board Hindi textbooks do print `E°सेल`, so this is a house choice rather than
an error — but subscripting Devanagari inside LaTeX needs XeLaTeX with
polyglossia, which this image does not have.

## Definitions: exact, then glossed

The definition itself is **textbook-exact** — that is what the student writes in
the exam, so it does not get casualised. The casual explanation comes
immediately after, opening with **“मतलब,”**.

```
“तो जब विद्युत्-अपघटन के दौरान किसी इलेक्ट्रोड पर मुक्त होने वाले पदार्थ की
 मात्रा, प्रवाहित विद्युत् की मात्रा के समानुपाती होती है।”
“मतलब, जितनी अधिक विद्युत् प्रवाहित होगी, उतनी ही अधिक मात्रा में पदार्थ
 इलेक्ट्रोड पर मुक्त होगा।”
```

Standard opener for a definition beat, in both samples:

> “सबसे पहले समझते हैं—<पद> किसे कहते हैं?”

## Tell them to focus *before* the important part

An attention cue goes **ahead of** the definition or the tricky point, never
after — and it always carries a reason, so it earns the attention:

> “और इसे ध्यान से समझना, क्योंकि अगर परीक्षा में बिल्कुल ऐसा ही लिख दिया, तो
> आपके नंबर पक्के हैं।”  ← stakes

> “और यहाँ एक बात ध्यान से याद रखना—बहुत सारे बच्चे यहीं गलती करते हैं।”
> ← the common mistake

> “ये याद रखना, यहाँ संबंध विद्युत् की मात्रा और मुक्त पदार्थ की मात्रा के बीच है।”
> ← the thing that gets confused

The reason is the point. A bare "ध्यान से सुनो" is not the house style.

## Register

Casual spoken Hindi, class 12, the way a teacher talks — but the subject's
**terminology and nomenclature never change**. विद्युत्-रासायनिक तुल्यांक,
समानुपाती, निरक्षीय स्थिति, द्विध्रुव आघूर्ण stay exactly as they are.

- **Em-dash `—` is the house connector**, used where English would use a comma,
  colon or dash: "सबसे पहले समझते हैं—", "पहला—धातु की प्रकृति", "इसलिए—".
- **आप / तुम mix** is correct: "आपकी परीक्षा", "आपके नंबर पक्के हैं" alongside
  "समझना", "याद कर लो", "जुड़ो".
- **Enumerate explicitly**: "पहला—…, दूसरा—…, तीसरा—…", then close with
  "बस, इन तीनों को याद रखो—…".
- **Memory aids**: "इसे याद रखने का आसान तरीका है", and word-equations like
  "धातु + वायुमण्डल की गैसें + नमी = संक्षारण।"
- **Curly quotes** `“ ”`, not straight ones.
- Say *why*, not just *what*: "धन आवेश हमेशा दूर धकेलता है, इसलिए …".

## The opening hook

Names the board, the class, the year(s), and **त्रैमासिक परीक्षा** — both samples
use that word, not a bare परीक्षा:

> “एमपी बोर्ड कक्षा बारहवीं के बच्चों! ये सवाल दो हज़ार पच्चीस में आ चुका है और
> इस साल भी आपकी त्रैमासिक परीक्षा में आ सकता है।”
> “और इस वीडियो के अंत तक आप इसे पूरा याद करके, परीक्षा में सही तरीके से लिखना
> भी सीख जाओगे।”
> “तो चलिए।”

Multiple years — first in full, middle shortened, last in full:

> “ये सवाल दो हज़ार उन्नीस, इक्कीस और दो हज़ार तेईस में आ चुका है …”

When the source is unsure which of two years it appeared in, the samples use
**या**, not और: "ये सवाल दो हज़ार तेईस या दो हज़ार पच्चीस में आ चुका है".

## The closing

Fixed, and both samples end the same way:

> “अब इसे परीक्षा में कैसे लिखना है, इसका पूरा उत्तर आपकी स्क्रीन पर आ जाएगा।”
> “इसे सेव कर लेना और इसका स्क्रीनशॉट लेना मत भूलना।”
> “और ऐसे ही आसान और मजेदार तरीके से पढ़ने के लिए अरिहान के ‘उन्नति बैच’ से जुड़ो।”

## Numbers: two rules, and they differ

A digit never survives in a **spoken** line, but what it becomes depends on the
kind of number:

| kind | written | spoken |
|---|---|---|
| **Years, class — Hindi words** | `2026` | "दो हज़ार छब्बीस" |
| | `2022` | "दो हज़ार बाईस" |
| | `कक्षा 12वीं` | "कक्षा बारहवीं" |
| **Algebraic values — English** | `2l` | "two-ell" |
| | `2p` | "two-p" |
| | `2E₁` | "two-E-one" |

The number and its variable are one spoken token — "two-ell", not "दो एल".
Operators around it stay Hindi: बटा, गुणा, जोड़, वर्ग, घन, कोस थीटा.

**Digits stay on screen** — the title card reads `वर्ष 2022` and equations
render as `2l`. This rule governs the mouth only. If a HeyGen voice mispronounces
a Latin token, the fallback is Devanagari phonetics ("टू-एल").

> The two verified samples in `style/samples/` still write years as digits
> (`2023`, `2025`) because they predate this decision. Follow the table above.

## Animation direction

The verified samples carry only `On Screen:` plus the formula — they were written
for a human editor. For this pipeline each beat also gets an English ANIMATION
block, which is never spoken and exists to generate Manim:

```
ANIMATION
  SHOW:     every object on screen this beat
  BUILD:    timed sequence — 0.0s … · 1.5s … · 3.0s …
  CRITICAL: the one thing that must not be drawn wrong (optional)
  HOLD:     what carries into the next भाग, so it is not redrawn
  AREA:     top 60%   (physics; the reels format uses 50%)
```

## Before writing: verify the source answer

The sheet's answer is a starting point, not the authority. Check every value,
count, position and relation against NCERT, and flag any mismatch in the script
rather than reproducing it.

Real case: PHY-C1-NM-01's answer states `E₁ > E₂`. On the equatorial line
`AP = BP`, so `E₁ = E₂` — and the whole derivation depends on that equality. The
script was written correctly and the discrepancy noted for the verifier.
