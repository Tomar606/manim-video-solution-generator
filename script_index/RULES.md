# What a script writer has to know

Rules distilled from four independent readings of all 111 shipped scripts. Each
one is a pattern the corpus follows, not a preference. Raw notes, unedited, are in
`observations.json`; the moves themselves are in `INDEX.md`.

---

## 1. The question's own verb decides the shape of the script

This is the single most load-bearing rule, and all four passes found it separately.

| The question says | The script must be |
|---|---|
| सिद्ध कीजिए · निगमन कीजिए · व्यंजक स्थापित कीजिए | numbered equations built in order, called back by number, with a final flow recap |
| अन्तर लिखिए · तुलना कीजिए · स्पष्ट कीजिए | fixed headings, both sides run in the same order every time, the sides never swap |
| सचित्र · चित्र सहित | the figure is the spine, and it is labelled |
| उदाहरण सहित | the textbook's own example, named |
| क्रियाविधि · प्रक्रिया · वर्णन कीजिए | numbered steps, each step restated in the running order |
| कारण सहित · क्यों | every claim carries a क्योंकि |
| परिभाषा · किसे कहते हैं | the exam-exact sentence first, then the plain gloss |

Quote the question's own word back to the student and say what it obliges
(`teach.question_wording_callback`). It also decides how many parts there are:
**the part count follows what the question demands, not the word count.**

## 2. Counts are a contract

If the opening says "तीनों चीजें" or "चार अलग-अलग कारण", then exactly that many
items follow, each announced (पहला / दूसरा / तीसरा), with a progress line between
them ("दो हो गए, अब तीसरा"), and the closing recap replays them in the same order.

Breaking the count is the most visible error a script can make. One script in the
corpus teaches three salt-bridge functions for a question that asks for two — that
is a defect, not a variation.

**Marks are the same kind of loop.** Where the opening promises "चार नंबर पक्के",
the closing says the same number back. 4 for Long Answer and derivations, 3 for
Short Answer. If the mark value isn't known, leave the promise out rather than
guess.

## 3. The teaching unit is a pair, and the order never inverts

1. the textbook sentence, exactly as the student must write it
2. immediately after, the plain restatement, opening with मतलब or यानी

The gloss is always shorter than the book line and drops the qualifiers. The
on-screen card belongs to the gloss, not to the book sentence. In the corpus this
pair (`teach.book_then_gloss`) appears in 79 of 111 scripts.

## 4. Everything on screen is spoken; not everything spoken is on screen

No formula, equation, chemical name or symbol ever appears on screen without a
companion line that reads it aloud in words (`teach.formula_readout`, 44 scripts).
An ON SCREEN equation with no spoken twin is a defect.

**Three read-out dialects exist and must not be mixed inside one script:**

| Dialect | Example |
|---|---|
| Devanagari transliteration, often under a literal `स्पोकन:` label | "वी बराबर एक बटा चार पाई एप्सिलॉन नॉट" |
| English symbol names in a Hindi frame | "V one बराबर है one by four pi epsilon naught K" |
| Full English spell-out with bracket structure (chemistry) | "Potassium four, open bracket Fe, open bracket C N, close bracket six" |

One physics script mixes two of them and reads as if two different people wrote it.
Also watch homophones: in Devanagari, `VR` and `Vr` become the same sound.

On-screen blocks **organise** — arrow chains, A/B pairs, numbered cards, a closing
revision table — they never retype the spoken sentence. Typically 3–6 words per node
against a 25-word spoken line.

## 5. The two registers never mix

| | Default (most of the corpus) | Formal batch (about 9 chemistry SA scripts) |
|---|---|---|
| Address | बच्चों, तुम-form (समझ लो, याद रखो) | आप-form, -इए (लिखिए, समझिए), with a बच्चों vocative only at the open |
| Hooks | mistake flags, memory metaphors, warmth | none |
| Sign-off | full stack | reduced or absent |

Pick one per script and hold it. One script mixes both and is the only register
break in the corpus.

## 6. The closing is a fixed block — assemble it, don't write it

**Current (the large majority):**
1. the question is done — "ये सवाल भी पूरा हो गया"
2. optional: remember-this-and-you-won't-forget
3. the exact answer is on the **Notes button** (on the right of the screen)
4. keep watching the study reels → finish the syllabus → 90%

**Deprecated (two of the oldest chemistry scripts):** answer appears on screen →
take a screenshot → join the उन्नति बैच. These also promise the *त्रैमासिक*
exam rather than the board exam. Never blend the two blocks.

Only part 1 carries the board/year opening, and only the final part carries the
closing.

## 7. Every part must stand alone, because every part is its own reel

- Part 2+ opens by naming what the previous part established (`bridge.recap_result`,
  65 scripts). In derivations it re-prints the equation that was reached.
- Every non-final part closes by naming both what is done and what is still owed
  ("X हो गया, अब Y बाकी"), usually with "Part N ज़रूर देखना".
- A part boundary is earned: it never falls mid-substitution or mid-explanation.
- If a part ends on an open question, the next part should reopen and answer it.
  Seven scripts pose a cliffhanger and only one ever re-asks it — copy the one.

## 8. Hindi carries the content, English carries the talk about the content

- Discourse words stay English in Latin script: *important, definition, exam,
  answer, point, step, formula, concept, clear, revise, syllabus*.
- Teachable nouns are Hindi first, English glossed after यानी or in brackets:
  "उल्बवेधन यानी Amniocentesis", "अपरद या डेट्रीटस (Detritus)". Never the reverse.
- Frozen terms stay exactly as the book writes them.
- Physics narration spells Latin variables as Devanagari words (एल for *l*, क्यू
  for *q*, एप्सिलॉन नॉट for ε₀) while keeping them Latin on screen. Greek letters
  are introduced by name before use ("κ यानी Kappa").
- **Romanised Hindi** ("toh bacho part 3 bilkul bhi miss mat karna") appears in
  several files. It is a typing artefact, not house style — the same presenter
  writes the same words in Devanagari elsewhere. Always generate Devanagari.

## 9. Examples come from the book, not from imagination

Only 2 of 111 scripts invent an everyday analogy. The examples are the textbook's
own instances — ocean biomass, insects on one tree, CH₃COOH for Kohlrausch,
NH₄NO₂ for a first-order reaction — because that instance is what earns the mark.

Where intuition is needed, the corpus decodes the term's own name
(`teach.name_unpack`) or gives a mnemonic (`hook.mnemonic_trick`) instead.

## 10. About one line in four is meta, and that ratio is the voice

Lines about the exam, the answer sheet, the marks or what to write — rather than
about the subject — cluster at the seams: before a definition, after a summary, at
every part boundary. Too few and it reads like a textbook; too many and it reads
like an advertisement.

Emphasis always carries a reason ("ध्यान से सुनना, **क्योंकि** परीक्षा में इसकी
परिभाषा से ही शुरुआत करनी है"). A bare "ध्यान से सुनो" is not the house style.

## 11. Repetition is deliberate

The running order is re-spoken after nearly every step, and in derivations the
final part re-shows every equation with its gloss before a one-line summary. For a
reel where a viewer can arrive mid-way, near-duplication is intended.

The limit: two scripts repeat a whole part with no new content. That is padding.

## 12. These scripts are drafts for a human presenter, not TTS-ready text

Spoken lines in the corpus are full of digits, units and symbols — "4 नंबर",
"46 गुणसूत्र", "95.6%", "8.85 × 10⁻¹² C² N⁻¹ m⁻²", "5'→3'". The presenter reads
them correctly; a TTS voice would not.

Take structure from this corpus, never TTS-readiness. Anything generated has to
spell numbers and symbols out in words.

---

## What the corpus does NOT contain

Worth knowing before assuming a move exists:

- **No real-life analogies** (see rule 9).
- **No opening curiosity question.** Not one script opens by asking the student
  something; every complete script opens on the board/year line or, where no year
  exists, on an importance or chapter frame.
- **No figure discipline.** Only one script carries an explicit figure placeholder
  with its labels named. Others say "diagram को ध्यान से समझना" and supply nothing,
  leaving the renderer to invent the geometry. If the question says सचित्र, the
  script has to name the figure and its labels.
