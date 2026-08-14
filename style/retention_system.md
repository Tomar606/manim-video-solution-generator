# Retention, hook and part-structure system

The authority for how a script *opens*, why a student *keeps watching*, where it
*breaks* into parts, and how the next part *re-enters*. The house voice and
format live in `pyq_script_format.md` and `NOTES.md`; this file governs
structure and retention.

## The golden rule

The student must never feel *"this is trying to keep me watching."* They should
feel *"I understood that, and now I genuinely want the answer to the next
question."*

## Priority order — never reversed

1. Correctness
2. Educational clarity
3. Conceptual progression
4. Student comprehension
5. Retention
6. Variation
7. Dramatic effect

A creative hook that makes the explanation worse is a bad hook. **A repetitive
but highly relevant hook beats forced novelty.**

## Hook mechanisms

| mechanism | use when | example |
|---|---|---|
| **exam_fomo** | the question genuinely repeats in boards; real marks value | "एमपी बोर्ड में फैराडे के नियमों से सवाल पहले भी पूछा जा चुका है। लेकिन इस सवाल में एक ऐसी बात है जिसे सही लिखना बहुत जरूरी है।" |
| **prediction** | the concept explains an observable consequence | "अगर किसी गैस का तापमान बढ़ा दिया जाए, तो उसका दाब किस तरह बदलेगा?" |
| **challenge** | the student could reasonably answer before learning it | "अगर विद्युत् की मात्रा दोगुनी कर दें, तो मुक्त पदार्थ की मात्रा कितनी होगी?" |
| **mistake** | students genuinely confuse two things, or misuse a formula | "फैराडे का पहला नियम याद करते समय एक गलती बच्चे अक्सर करते हैं।" |
| **contradiction** | intuition differs from the result; two laws seem to clash | "ज्यादा विद्युत् का मतलब ज्यादा पदार्थ — लेकिन क्या यह हर स्थिति में सही है?" |
| **analogy** | the concept is abstract and a real analogy genuinely simplifies it | — never force one into a technical topic; it breeds misconceptions |
| **payoff** | procedural content, clear exam outcome, little natural curiosity | "आज सिर्फ दो नियम समझने हैं, लेकिन अंत तक आप इन्हें परीक्षा में पूरा उत्तर बनाकर लिख पाओगे।" |
| **problem** | the concept is a tool; the application is more interesting than the definition | — |

**Never manufacture exam relevance** where it is weak, and never claim a mistake
is common unless it plausibly is.

### Choosing by topic type

| topic_type | prefer |
|---|---|
| definition | payoff · mistake · simple curiosity — no forced cliffhanger |
| law / principle | prediction · challenge · contradiction · application |
| formula | prediction · challenge · problem |
| derivation | problem · payoff · partial reveal |
| numerical | challenge · prediction · mistake |
| process | curiosity · prediction · story · sequential question |
| comparison | contradiction · challenge · prediction |
| exception | surprise · mistake · contradiction |
| diagram | prediction · question · visual-first |
| exam_answer | marks/payoff · mistake · direct outcome |

Chemistry order of preference: prediction, mistake, exam_fomo, challenge,
contradiction, analogy.

## The assigned mechanism must be the actual opening

The approved samples all open on the board/class/year line, because they happen
to use `exam_fomo`. Left to itself the model copies that opening whatever
mechanism it was given, and reports the assigned mechanism in the META line
anyway — five physics scripts in a row began with the identical sentence.

So when the mechanism is anything other than `exam_fomo`, the FIRST spoken line
is that hook and the exam line comes SECOND. `check_script` fails a script whose
opening line carries the board or year phrase under any other mechanism.

## Banned

Generic clickbait of any kind: "आप यकीन नहीं करेंगे", "आगे जो होगा",
"इसका जवाब आपको चौंका देगा", "99% बच्चे ये नहीं जानते",
"वीडियो के अंत तक जरूर देखना". Also: artificial suspense, fake urgency,
excessive rhetorical questions, and *repeated* "बच्चों", "आज हम सीखेंगे".

**"ध्यान से सुनो" is not banned — repeating it is.** The team's note on the
first batch was that the scripts read too formal. The rule that came out of it:

> **Subject matter formal, connective tissue casual.**

The teaching keeps its register; the sentences between the teaching should sound
like a person talking — "चलो इतना हो गया? अब आगे बढ़ते हैं", "इस बात को दिमाग
में बिठा लो", "नेक्स्ट पार्ट में मिलते हैं", "फॉलो कर लो". Casual never means
mocking or talking down.

The full table of what to avoid and what to say instead is in `NOTES.md`, and
the approved alternatives for each recurring moment are in `variations.yaml`.
Use a different one each time.

## Rhythm, not a template

```
HOOK → SETUP → EXPLANATION → retention beat → EXPLANATION
     → PART BREAK → RE-ENTRY → EXPLANATION → PAYOFF → CTA
```

This is a frame, not a form. **Do not put a retention beat after every
section.** The video must still feel like a teacher explaining something.

Intensity: LOW for dense concepts that need concentration · MEDIUM for most
videos · HIGH only when the topic is dry, long, or multi-part. Never HIGH
throughout — the viewer needs stretches of ordinary teaching.

## Part breaks

Split at a **cognitive** boundary, never on a timer: a concept fully
established, a question raised but unanswered, a formula derived with
application still to come, explanation done and exam-writing next.

Never split mid-explanation, and never invent a cliffhanger where nothing is
genuinely unresolved.

**Transition mechanisms:** `open_loop` · `question_carryover` · `contradiction`
· `cliffhanger` (sparingly) · `partial_reveal` · `future_payoff` ·
`challenge` · `direct_continuation`.

`direct_continuation` matters: **not every part needs a dramatic ending.**

**Re-entry mechanisms:** `answer_first` · `callback` · `direct_continuation` ·
`recap_question` · `visual_first` · `resolution_first`.

**Do not recap merely because it is Part 2.** Recap only when the previous
concept is needed, the connection is meaningful, or the previous part closed on
a question that needs answering.

## Variation happens at six levels

mechanism · angle (curiosity, marks, confidence, surprise, relief, discovery,
usefulness) · framing (question vs scenario vs statement) · language ·
placement (hook first vs question after setup) · transition.

So a small set of strong mechanisms produces plenty of variety. Reuse a
mechanism when it is genuinely the best fit — but **never reuse the wording**.
The objective is not "never repeat a hook"; it is "never let the student feel
they are watching the same template again."

## History is a preference, not a ban

`style/hook_history.json` records recent mechanisms, angles and phrasings.
Selection order: topic relevance → educational suitability → naturalness →
recent usage. If the best hook matches the last video's, use it anyway and vary
the expression. If two are equally suitable, prefer the less recently used.

## CTA is not a retention device

The educational payoff lands *before* the CTA:
concept → exam payoff → summary → CTA. Never follow "अगले पार्ट में समझेंगे"
straight into promotion.

## Metadata

Every script carries, but never exposes, a block like:

```json
{
  "topic_type": "law",
  "hook_mechanism": "prediction",
  "hook_angle": "curiosity",
  "transition_mechanisms": ["question_carryover", "future_payoff"],
  "part_opening_mechanisms": ["answer_first", "direct_continuation"],
  "retention_intensity": "medium"
}
```

## QA before finalising

**Hook** — related to the topic? mechanism right for the type? genuine reason to
continue? free of clickbait? wording not recently used?
**Transition** — boundary cognitively natural? question genuinely unresolved?
actually paid off next part? would plain continuation be better?
**Re-entry** — connected? recap actually needed? not repetitive?
**Overall** — too many rhetorical questions? too many suspense devices? does it
still sound like a teacher? is the *content* doing the retention work?
