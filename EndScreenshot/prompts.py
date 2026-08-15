"""Every prompt EndScreenshot sends, in one place.

Ported from the sibling ``notes-editor`` repo (``handwrite.py``). Two prompts
drive the two generation steps:

``TEMP_PROMPT``    step 1 — mint the base sheet ("the temp"). notes-editor
                   calls this on a *written* sample page to erase its ink; we
                   call it on an already-blank sheet, where its real job is to
                   re-photograph the paper through the same model that will
                   write on it. A flat synthetic PNG and a model-native page
                   composite very differently in step 2.
``MASTER_PROMPT``  step 2 — write the question and answer onto that sheet in
                   the reference hand. This is master prompt V32 verbatim, the
                   revision approved in notes-editor.

Bump ``PROMPT_VERSION`` when MASTER_PROMPT changes and snapshot the old text,
the same discipline notes-editor keeps in its ``master-prompts/`` folder.
"""
from __future__ import annotations

# Matches notes-editor's handwrite.py PROMPT_VERSION at the time of the port.
PROMPT_VERSION = 32
TEMP_PROMPT_VERSION = 3


# --------------------------------------------------------------------------- #
# Step 1 — the temp (base sheet)                                               #
# --------------------------------------------------------------------------- #
# notes-editor's _BLANK_PROMPT. The "erase every trace of ink" instruction is
# kept even though our input is already blank: it costs nothing on a clean
# sheet, and it means the same prompt works if someone points EndScreenshot at
# a photographed page that happens to have writing on it.
TEMP_PROMPT = """This is a scanned page from a student's notebook. \
ERASE every trace of ink from it: all handwriting, all headings, all \
highlighter marks, all doodles, and any large semi-transparent diagonal \
WATERMARK text or logo stamped across the page. Output the SAME page \
completely BLANK. (If the page is already blank, simply return it as it is — \
same paper, same lines, nothing added.)

⚠️ DO NOT IMPROVE THE PHOTO IN ANY WAY (CRITICAL): do NOT brighten, whiten, \
clean, de-noise, sharpen, colour-correct, flatten or "fix" the page. Keep the \
EXACT same exposure and darkness, the same slightly warm / off-white paper \
tint, the same uneven lighting, soft shadows, grain, smudges, scanner \
artefacts and paper texture as the input photo — reproduce them faithfully. \
If the original scan is a bit dim, dull or yellowish, the output must be \
exactly that dim, dull and yellowish. The result must look like the SAME \
photograph of the SAME sheet, just taken before anyone wrote on it — NOT a \
cleaner, brighter or fresher page.

KEEP unchanged, exactly as in the input photo: the paper colour and texture, \
the printed horizontal ruled lines, their exact spacing and count, the \
printed red/pink vertical margin line(s) if any, the page edges, and the scan \
lighting with its soft shadows. Nothing redrawn, nothing added, no text or \
watermark of any kind anywhere.

⚠️ THE RULED LINES ARE THE POINT: they must come out crisp, evenly spaced, \
perfectly parallel and running the full width of the writing area, exactly as \
many of them as the input has. Do not thicken, blur, recolour, re-space, add \
or drop a single rule."""


# --------------------------------------------------------------------------- #
# Step 2 — the master prompt (notes-editor V32)                                #
# --------------------------------------------------------------------------- #
MASTER_PROMPT = """You are given TWO images.

IMAGE 1 is a BLANK NOTEBOOK PAGE — a real sheet from a student's notebook \
(its paper colour/texture, its printed horizontal ruled lines and the scan's \
natural lighting are all real pixels). This exact page is the one you WRITE ON.

⚠️ PRESERVE THE BASE PAGE EXACTLY (CRITICAL): this is an image-EDIT. Keep \
IMAGE 1's real pixels — paper, ruled lines, edges, shading — completely \
VISIBLE and UNCHANGED. Do NOT redraw, erase, recolour or crop the page, do \
NOT brighten, whiten, clean or colour-correct it, and do NOT add any new \
printed elements, boxes, logos or labels. ONLY add handwriting on top of it. \
The writing sits ON the printed ruled lines exactly like real notebook writing.

IMAGE 2 is a HANDWRITING STYLE REFERENCE — a page already written by the \
student whose notebook this is. COPY THAT HANDWRITING: the same letter \
shapes, slant, x-height, stroke weight, rhythm, the same pen colours used the \
same way (body ink colour, heading ink colour) and the same layout habits. \
This page must look like the SAME person on a different day — a TINY natural \
drift in slant/size/spacing is welcome, a photocopy-perfect clone is not. Do \
NOT copy IMAGE 2's words or sentences — only its hand and its colour habits.
⚠️ COPY THE LETTERFORMS EXACTLY (CRITICAL): STUDY IMAGE 2 and reproduce ITS \
specific letterforms — the exact way this writer draws their letters, their \
capitals, their joins, their slant and their word spacing habits. Do NOT \
substitute any other handwriting style, font-like script or "beautiful \
cursive" — a friend of this writer must instantly recognise the page as THEIR \
handwriting.
⚠️ If IMAGE 2 carries a watermark or logo, that is NOT part of the \
handwriting. IGNORE it totally and NEVER draw any watermark, stamp, logo or \
ghost text on the output page.

YOUR JOB: hand-write the CONTENT below onto IMAGE 1 in IMAGE 2's hand — a \
real student's notebook page, this is page {PAGE_NO} of {TOTAL}.

## CONTENT TO WRITE (render EXACTLY — do not change, translate, drop, \
shorten, summarise, repeat or invent a single word; spell every name, term \
and symbol exactly as given):

{CONTENT}

⚠️ WRITE ONLY THE TEXT ABOVE — NOTHING ELSE. No extra points, facts, \
examples or explanations from your own knowledge. If the content ends before \
the page is full, leave the rest of the page blank paper. One given line = \
one point, as written.

CONTROL TAGS — every content line starts with a tag in << >>. The tag says \
HOW to style the line. NEVER write the tag itself (never draw TITLE, SUBHEAD, \
TEXT, POINT, Q, ANS or << >> on the page). Only write the words after it.
* <<TITLE>>   → main heading, a bit larger/bolder, in the same ink colour \
IMAGE 2 uses for its main headings.
* <<SUBHEAD>> → section heading, slightly bolder, in the heading colour(s) \
IMAGE 2 uses.
* <<TEXT>>    → flowing sentence line(s) in the body ink, NO marker in \
front. A long <<TEXT>> is ONE paragraph: let it wrap naturally across as many \
rows as it needs, exactly like a written-out paragraph in a notebook.
* <<GAP>>     → not text: leave ONE ruled row completely EMPTY here \
(breathing space between topics) and continue on the next row. Never write \
anything for it, and never ignore it — these blank rows are what stop the \
page reading as one solid block.
* <<POINT>>   → one list item in the body ink with EXACTLY ONE marker in \
front. Use a plain imperfect DOT (•) for ordinary lists — that is the default. \
Numbers ((i), (ii)) are fine when the source numbers them. An ARROW (->) is \
ONLY for a genuine sequence or cause-and-effect flow, never as a decorative \
bullet. NEVER two markers combined.
* <<Q>>       → an exam QUESTION, written in BLACK pen (the muted warm \
near-black). NO bullet/arrow marker.
* <<ANS>>     → the ANSWER's opening, written in BLUE (body ink). NO \
bullet/arrow marker.

MARKERS ARE RARE (IMPORTANT): ONLY <<POINT>> lines get a marker. <<TEXT>>, \
<<Q>>, <<ANS>> and headings NEVER get arrows, dots or numbers.

LAYOUT (compact and organic):
* {FILL_NOTE}
* NEVER END A PAGE WITH A STRANDED HEADING: if the last thing that would fit \
is a heading with nothing under it, do not write that heading — carry it to \
where its content begins.
* WRITE ON THE RULED LINES (ABSOLUTELY CRITICAL): IMAGE 1's printed ruled \
line is the BASELINE. Every row of handwriting SITS on a ruled line, the way \
real notebook writing does — the body of each word rests ON the rule, rising \
above it, with only descenders dipping below. SIZE THE LETTERS TO THE RULED \
GAP: the letter body must be clearly SHORTER than the space between two \
rules. NEVER let a printed rule run through the middle of a word, and NEVER \
leave a row of text floating halfway between two rules.
* ONE ROW OF WRITING PER RULED LINE — NEVER TWO (CRITICAL): each ruled line \
carries exactly ONE row of text. Never squeeze a second row of words into the \
gap between two rules. If the remaining content does not fit the page at \
one-row-per-rule, it simply continues on the next page — running out of room \
is NEVER a reason to double up.
* LEAVE THE LAST RULED LINE OF THE PAGE BLANK.
* BASELINE CONTACT — NO FLOATING, NO EXCEPTIONS (CRITICAL): treat every \
printed rule as a physical SHELF: the bottoms of the letters physically REST \
on it, touching it, for EVERY single row on the page — including headings, \
the wrapped continuation of a long paragraph, and an indented line. If any \
row of text is hovering between two rules touching neither, it is WRONG.
* SMALL HAND (IMPORTANT): write NOTICEABLY SMALLER — the letter body \
(x-height) roughly HALF the gap between two rules. A compact, quick student \
hand, not large display writing. Still seated on the rules, still legible.
* Leave the notebook's natural top gap before the first line.
* DO NOT OVERCROWD (CRITICAL): write at a comfortable, natural revision-notes \
size with RELAXED, even line spacing — a clean, airy page that is easy to \
read. NEVER shrink the letters, tighten the spacing or squeeze lines together \
to fit more in.
* SAME DENSITY AT THE BOTTOM (CRITICAL): the LAST rows must have exactly the \
same letter size, row spacing and relaxed feel as the FIRST rows. A reader \
must not be able to tell top from bottom by density.
* When a point wraps, indent the wrapped line to align with the text above, \
not with the marker.
* RAGGED RIGHT EDGE (IMPORTANT): never justify. Each line ends where it ends. \
Word spacing uneven. It must read as handwriting, never as a typeset block.
* JAGGED LEFT EDGE (CRITICAL — do this strongly): line starts wander \
horizontally by small random amounts. A gently jagged, human left edge, never \
a ruler-straight column.

INK & COLOUR:
* MUTED, LOW-SATURATION ink only — real ballpoint/gel ink photographed on \
paper, never bright, electric or neon. Blue = dull dark navy/dusty blue; \
black = soft warm near-black; red = muted brick/maroon. Match the pen colours \
and their roles to IMAGE 2.
* Body text in the body colour IMAGE 2 uses (usually blue). ALL bullet \
markers in the body colour too — never red/black markers.
{HIGHLIGHT_RULES}

NATURAL HANDWRITING REALISM (THE WHOLE POINT — imperfection over neatness; \
the page must NEVER look like a font):
* VARIABLE PEN PRESSURE & INK FLOW (TOP PRIORITY, do it STRONGLY): stroke \
darkness and width vary constantly, even inside one word — down-strokes \
darker/thicker, up-strokes thinner/paler. Some words freshly dark, others \
noticeably paler where the pen ran fast or dry. Occasional DRY-PEN SKIPS \
(tiny white breaks inside long strokes). INK POOLING — small darker blobs \
where the pen starts, stops or turns. A few tiny stray ink dots, one faint \
smudge, a couple of letters visibly retraced.
* NON-UNIFORM LETTERS (CRITICAL): every occurrence of the same letter on the \
page must be drawn a VISIBLY different way — a different exact shape, loop \
size, width, tilt and height each time. NEVER the identical glyph repeated. \
The same WORD written twice must not look like a photocopy of itself. Strokes \
are a little shaky, loops don't close perfectly. Hand-made and slightly \
wobbly, never machine-smooth, yet fully legible.
* REPEATED PHRASES (ABSOLUTELY CRITICAL — this is THE tell-tale of fake \
handwriting): when the same word or phrase appears on several lines, each \
occurrence must look written AFRESH by hand — clearly different letter \
shapes, a slightly different size and slant, different word spacing, a \
different indent from the margin, the baseline a touch higher or lower. If \
two lines could be overlaid and match, it is WRONG.
* SLANT / BASELINE / SPACING drift: slant wanders line to line; baselines \
drift gently; letter size and word gaps vary; a word near the right edge gets \
squeezed or spills slightly; one or two lines look rushed and more cramped.
* SELF-CORRECTION — the page carries EXACTLY ONE, and it is given to you as a \
marker: [[FIX wrong|right]]. Wherever you see [[FIX abc|abcd]] in the content, \
write it like a writer catching a slip: write the FIRST word ("abc"); cross it \
out completely with one quick slightly slanted stroke; then write the SECOND \
word ("abcd") clearly and in full immediately after it. Never draw the \
brackets, the bar, or the word "FIX". The two words are DIFFERENT — draw \
exactly the letters given for each.
  ⚠️ BOTH WORDS MUST APPEAR — do NOT merge them into one. A single struck \
word with nothing legible after it is a FAILURE.
  Create NO other corrections anywhere on the page: no other word may be \
struck, and nothing may be inserted above a line with a caret.
  ⚠️ FORBIDDEN: NEVER strike out a word that is already spelled CORRECTLY. \
NEVER strike a word and follow it with a DIFFERENT word. NEVER leave a struck \
word with nothing after it. NEVER strike only PART of a word. Keep \
corrections to ordinary WORDS — never strike or rewrite a number, variable, \
index, symbol or any part of an equation.
  ⚠️ READ-BACK CHECK before you finish: read the page ignoring every \
struck-out word. What remains MUST equal the given text WORD FOR WORD — \
nothing missing, nothing duplicated, nothing added.

MATHS NOTATION (when the content has algebra, equations or working):
* Write mathematics the way it is meant to READ, never as flat computer text. \
Powers are small RAISED digits (x², not "x^2"); subscripts are small LOWERED \
ones (K_f drawn as K with a small low f); Greek letters are drawn as letters \
(Δ, π).
* A FRACTION is written with a horizontal bar — numerator above, denominator \
below, the bar drawn freehand and slightly wavy. Give a fraction the vertical \
room of two ruled rows.
* Keep every symbol exactly as given: = ≠ ≤ ≥ ± × ÷ → ⇒ ∴ ∵ and brackets.
* Copy every coefficient, index, sign and term EXACTLY. A maths slip is a \
content error, not a realism feature.
* A line that is pure ENGLISH letters or MATHS symbols sits vertically \
CENTRED in the gap between two printed rules, touching neither — unlike \
Hindi, which hangs from the rule above. IMAGE 3 places every such line \
exactly where it belongs; keep it there.

If any content is in HINDI (Devanagari): write it with a clean continuous \
शिरोरेखा head-line per word (hand-drawn, not perfectly straight), correct \
matras and half-letters, English words sitting on the same baseline.

Output a single image: IMAGE 1 with the content hand-written on it, and \
nothing else changed."""


HIGHLIGHT_OFF = """* NO DECORATIVE HIGHLIGHTING: do NOT highlight headings or \
any line on your own initiative — no neon swipes, no coloured wash behind \
words."""

HIGHLIGHT_ON = """* HEADINGS may carry the same kind of highlighter swipe \
IMAGE 2 uses: apply it ONLY where the sample would — a single quick uneven \
swipe, slightly overshooting or falling short of the words, semi-transparent, \
never neat or rectangular. Body text is NEVER highlighted."""


# --------------------------------------------------------------------------- #
# Measured page-fill notes                                                     #
# --------------------------------------------------------------------------- #
FILL_FULL = """PAGE FILL (measured): this page's content was MEASURED against \
the page's ruled lines and fills the page. Start on about the 3rd ruled row \
and write one row of text per ruled line, steadily, to the BOTTOM — the last \
content line should land near the lowest ruled rows. Do NOT stop early leaving \
a blank lower area, and do NOT shrink or stretch the writing."""

FILL_SPREAD = """PAGE FILL (measured): this page's content was MEASURED \
against the ruled lines and comes to about {PCT}% of them — a little short of \
a full page. Do NOT leave the bottom empty and do NOT add anything: instead \
SPREAD the same content gently over the whole page. Start on about the 2nd \
ruled row and use slightly more generous line spacing throughout — an extra \
blank ruled row between sections, a little more air above a heading — so the \
writing finishes NEAR THE BOTTOM. Keep the spreading EVEN from top to bottom, \
keep the letters their normal size, and never stretch words to fill a line."""

FILL_PARTIAL = """PAGE FILL (measured): this is the LAST page and its content \
was MEASURED to fill roughly {PCT}% of the ruled rows. Start on about the 3rd \
ruled row, write one row of text per ruled line at the same steady size as \
usual, and simply STOP where the content ends — leave the rest of the page as \
blank ruled paper. Never stretch or pad the writing."""


# --------------------------------------------------------------------------- #
# Job-specific overrides                                                       #
# --------------------------------------------------------------------------- #
# The supplied sheet has horizontal rules only. The master prompt tells the
# model to park "Q1:"/"Ans:" left of a vertical red margin rule that does not
# exist here, which leaves the labels floating off the text block.
NO_MARGIN_OVERRIDE = """* THIS PAGE HAS NO VERTICAL MARGIN LINE — only \
horizontal ruled lines. So do NOT try to write anything "out in the left \
margin". The question label ("Q1:") and the answer label ("Ans:") are written \
INLINE, at the normal left text edge, immediately followed by their text on \
the same row. Nothing is written left of the text column.
* The <<Q>> line is the first thing on page 1, in black pen. The <<ANS>> \
line's "Ans:" label is in black, and the answer text after it is in the blue \
body ink."""

ANCHOR_NOTE = """

IMAGE 3 is an EARLIER PAGE OF THIS SAME NOTEBOOK, written by the same \
student. Your page must look like it came from the same notebook on the same \
day: the SAME letterforms, the same letter SIZE, the same slant, the same \
line spacing and the same ink. ⚠️ Copy only its HANDWRITING — never its \
words, sentences or layout."""


# --------------------------------------------------------------------------- #
# Step 2 override — the mock-up is the blueprint                               #
# --------------------------------------------------------------------------- #
# Ported from notes-editor's draw_from_mockup_irreg.py. This is what turns the
# typeset temp into a layout instruction: the model no longer has to work out
# how much fits, where a line breaks, or how far down to stop — it can see it.
# Adapted in one place: their sheet has a printed red margin rule to measure
# indents against and ours does not, so those references are to the left edge.
MOCKUP_LAYOUT = """* IMAGE 3 IS THE LAYOUT OF THIS EXACT PAGE, already typeset on this same
  ruled sheet. It is a BLUEPRINT, not something to copy the look of. Follow
  it EXACTLY:
    - the same lines in the same order, on the SAME ruled rows;
    - each line BREAKS at the same word it breaks at in IMAGE 3, and a
      sentence that continues on the next row starts at the same indent;
    - the same rows left blank between topics;
    - the page ENDS where IMAGE 3 ends — do not add, stretch or invent
      anything to fill what is left, and do not stop early either.
  If your handwriting is running wider than IMAGE 3's typed line, keep the
  same words on that row and let the right edge stay ragged; never drop a
  word and never shrink your letters to catch up.
* COPY IMAGE 3's IRREGULARITY, NOT JUST ITS WORDS. This is a real student's
  notebook, not a printed book, and IMAGE 3 already shows you exactly where
  the hand wandered — reproduce it:
    - THE LEFT EDGE IS RAGGED. Each paragraph begins at a slightly different
      distance from the left edge, exactly as IMAGE 3 shows. The bullet dots
      MUST NOT line up on one vertical — some start a few millimetres
      further in than others. Do not tidy this up.
    - The bullet dots sit at VISIBLY DIFFERENT distances from the left edge;
      look at how far each one is indented in IMAGE 3 and reproduce that
      difference. Aligning them into a column is the most common way this
      page ends up looking printed.
    - Word spacing is uneven — never the same gap twice in a row.
    - Letter size wavers a little from word to word and the pen presses
      harder in some places than others.
  Do NOT regularise any of this into a neat grid. A page where every line
  starts on the same vertical looks printed, and is wrong.
* IMAGE 3 is TYPED only so the layout is legible. Your page is HANDWRITTEN
  throughout in the hand of IMAGE 2 — never imitate the typeface, and never
  leave any printed-looking text on the page.
* ⚠️ INK COLOUR COMES FROM IMAGE 3 ONLY — NOT FROM IMAGE 2 (the previous
  attempt wrote the WHOLE page in blue and was rejected). IMAGE 2 is the
  reference for LETTERFORMS ONLY; ignore which colours it uses and where.
  Read the colour of each line off IMAGE 3 and reproduce it:
    - the "Q1:" label AND the whole question line: BLACK pen;
    - the "Ans:" label: BLACK pen;
    - every section heading (for example कार्यविधि, लाभ): BLACK pen;
    - everything else — the answer body and the bullet points and their
      dots: BLUE pen.
  Two pens are in use on this page. A page written entirely in one colour is
  WRONG. Before you finish, check that the question line and both headings
  are visibly BLACK against the blue body.
* Bullets: the same round hand-made dot in the same left position.
* ⚠️⚠️ HOW HINDI SITS ON A RULED LINE — THE MOST IMPORTANT RULE ON THIS
  PAGE, AND THE ONE THE LAST ATTEMPTS GOT WRONG. Devanagari is NOT written
  like English. English letters STAND ON the line. Devanagari HANGS FROM it:
    - The शिरोरेखा — the straight horizontal head-line along the TOP of every
      Hindi word — is drawn ALONG THE PRINTED RULE ITSELF. The head-line and
      the printed rule are the SAME line. The word's head-line lies exactly
      on top of the printed rule and follows it across the page.
    - EVERYTHING ELSE OF THE LETTER HANGS DOWN BELOW THAT RULE, into the gap
      underneath it. क, म, न, स, प, ब — the whole body of the letter is
      BELOW the printed rule, never above it.
    - Only the upper matras (ि ी े ै ो ौ ं ॅ) and the odd tall stroke poke
      up ABOVE the rule. Nothing else does.
    - So each ruled row is filled like this: printed rule at the TOP with the
      head-line running along it, letter bodies hanging beneath it, and the
      NEXT printed rule below them.
  DO NOT stand the Hindi letters on top of the rule the way English sits on
  a baseline — that leaves the writing floating in the middle of the gap and
  is WRONG. DO NOT let the writing hover between two rules touching neither.
  Look at IMAGE 2: that is a real Hindi notebook page and every word in it
  hangs from its rule exactly this way. Copy that relationship precisely.
* The Latin words on the page ("Berkeley and Hartley Method", "Q1:", "Ans:")
  share the Devanagari baseline — they sit level with the BOTTOM of the Hindi
  letters beside them, not on the printed rule.
* ⚠️ DO NOT REDRAW THE RULED LINES — THIS IS WHERE THE LAST ATTEMPT FAILED.
  You re-rendered the sheet with your OWN set of rules at your own spacing,
  slightly offset from IMAGE 1's, and then wrote between them. The result is
  writing that floats in the gaps, detached from every line. IMAGE 1's rules
  are REAL PIXELS: keep them exactly where they are, at the same count,
  spacing, thickness and faint colour. Add NOTHING but handwriting.
* EVERY LINE OF WRITING MUST TOUCH A RULE. Go row by row: the शिरोरेखा is
  drawn ALONG an existing printed rule so the two coincide, and the letters
  hang beneath it into the gap below. There must be NO visible gap between
  the top of a word and the rule it belongs to. If you can see white space
  between a word's head-line and the rule above it, the row is in the wrong
  place — move it up onto the rule.
* Count the rules in IMAGE 3 and use the SAME ones. Line 1 of IMAGE 3 is on
  the first rule; your line 1 goes on that same first rule, and so on down
  the page.
* LETTER SIZE IS FIXED AND NEVER CHANGES: the body of a letter is about half
  the ruled gap. ONE line of IMAGE 3 occupies ONE ruled row at that full
  size. NEVER shrink the writing to squeeze more on, or to reach the bottom.
  Where IMAGE 3 leaves the last rules blank, leave them blank.
* DEVANAGARI: copy every word letter-for-letter as IMAGE 3 spells it,
  including every conjunct and matra (अर्द्धपारगम्य, सरन्ध्र, समकेन्द्रिक).
  Draw the शिरोरेखा as one continuous hand-drawn head-line per word. Do NOT
  substitute a similar-looking letter and do NOT simplify a conjunct — a
  changed letter is a spelling error, not a handwriting variation.
* CORRECTIONS: only where IMAGE 3 shows a word struck through. If IMAGE 3
  shows none, this page has none — strike nothing.
* ⚠️ THE BINDU / ANUSVARA IS PART OF THE SPELLING, NOT DECORATION. Copy the
  dot above a word EXACTLY as IMAGE 3 has it — never add one, never drop one.
  This has gone wrong on every previous attempt: है and हैं are DIFFERENT
  WORDS (singular vs plural) and writing one for the other is a grammar
  error, not a handwriting variation. Go along the page and check each one:
  होती है, जाती है, होता है, रहता है, जाता है, लगता है, सकता है all end in
  है with NO dot; only नलियाँ होती हैं, लगाते हैं, भरते हैं, मिलते हैं take
  the dot. If IMAGE 3 shows no dot, do not draw one.
* HOW A REAL HAND WRITES DEVANAGARI — make it look WRITTEN, not typed (the
  last page came out looking like a printed font):
    - The शिरोरेखा is a SEPARATE PEN STROKE drawn across the top of each
      word, not a ruled bar. Its thickness varies along its length, it is
      never perfectly straight, it starts and ends slightly untidily, and on
      some words it breaks or does not quite reach the last letter.
    - Every occurrence of the same letter is drawn DIFFERENTLY — the क in one
      word is not the क in the next. Loops (in थ, फ, म, स) close by different
      amounts; some are a little rounder, some flatter, some taller.
    - Matras vary: the ि and ी hooks differ in height and curl each time; the
      े and ै strokes sit at slightly different angles; ु and ू tails vary
      in length.
    - Pen pressure changes constantly — downstrokes darker and thicker,
      some words noticeably paler where the pen ran dry, small ink blobs
      where a stroke starts or turns.
    - The same word written twice must NOT look identical. If two words could
      be laid on top of each other and match, it is wrong.
  Study IMAGE 2 — it is a real Hindi notebook page — and reproduce how that
  hand actually forms these letters, including its untidiness."""

MOCKUP_FILL_NOTE = ("Fill the page exactly as far down as IMAGE 3 does — "
                    "no further, no less.")

MOCKUP_ANCHOR_NOTE = """
* IMAGE 4 is an EARLIER PAGE OF THIS SAME NOTEBOOK. Your handwriting must
  look like it came from the same notebook on the same day: the same
  letterforms, size, slant and ink. Copy only its HANDWRITING — the layout
  comes from IMAGE 3 and the words from the content above."""


# --------------------------------------------------------------------------- #
# Diagrams — supplied verbatim by the user                                     #
# --------------------------------------------------------------------------- #
# The figure is pasted into the temp GHOSTED (faint grey). notes-editor learned
# that a crisp printed panel gets copied pixel-for-pixel instead of redrawn by
# hand — ghosting tells the model WHAT the figure is, WHERE it sits and HOW BIG
# it should be, while leaving nothing crisp enough to trace.
DIAGRAM_PROMPT = """DIAGRAM ON THIS PAGE — the faint grey figure printed in
IMAGE 3 is a REFERENCE, not artwork to reproduce. Redraw it yourself in that
exact position and at that exact size, following these requirements:

Your task is NOT to trace or recreate it perfectly. Instead, redraw it as if a
real NEET student hand-drew it in their old ruled notebook while studying.

DRAWING STYLE
- Everything must look genuinely hand drawn using a graphite pencil.
- No digital smoothness. No vector lines. No perfect geometry. No perfect
  symmetry.

LINES
- Pencil pressure must naturally vary throughout the drawing.
- Some lines should be darker, some lighter.
- Small hand jitters should exist. Curves should wobble slightly.
- Parallel lines should not remain perfectly parallel.
- Shapes should drift slightly from the reference while remaining
  scientifically correct.
- Do NOT use identical stroke thickness everywhere.

LABELS & TEXT
- Every label must be handwritten, in the same hand as the rest of the page.
- Handwriting should resemble that of a hardworking NEET student, not
  calligraphy.
- Slight variation in letter size, slant, spacing and baseline. Some letters
  may be a little taller or wider. Pencil pressure should vary naturally.
- Text should never resemble a digital font.
- Maintain readability while allowing natural imperfections.
- Spell every label EXACTLY as the reference spells it — copy each one letter
  for letter from the faint figure and use NO others. Never guess a word from
  the faint guide: a label you cannot read is copied stroke by stroke, not
  replaced with a similar-looking word. When the job's overrides list the
  labels in full, those strings are the ONLY text in the figure.

ARROWS
- Draw arrows by hand. Arrow shafts should not be perfectly straight.
- Arrowheads should vary slightly in angle and size.
- Different arrows should look individually drawn rather than copied.

REPETITIVE STRUCTURES
If the diagram contains repeated blocks, cells, membranes, dots, fibers,
organelles, etc.:
- Every repetition must be slightly different.
- Introduce tiny variations in spacing, size, orientation and shape.
- Avoid any copy-paste appearance.
- Make it obvious that each element was drawn individually by hand.

STRUCTURES
- Preserve the scientific meaning and overall layout from the reference.
- Small inaccuracies in outline are acceptable and encouraged.
- Avoid mathematically perfect circles, ovals or polygons.
- Organic structures should appear naturally irregular.

SHADING
- Use extremely minimal pencil shading only where necessary.
- No colored pencils. No ink. No markers. No heavy gradients.
- Mostly clean line work.

REALISM
The figure should convincingly look like a real student's notebook, drawn
during exam preparation, photographed or scanned from the notebook — NOT
AI-generated, NOT digitally illustrated, NOT traced.

Most important: the drawing should feel slightly imperfect everywhere. Humans
unconsciously introduce tiny inconsistencies in every stroke, letter, arrow,
curve and repeated structure. Those imperfections should be present throughout
the entire diagram while preserving scientific accuracy and readability.

⚠️ THE TEXT WRAPS AROUND THE FIGURE. IMAGE 3 shows lines of writing running
BESIDE the diagram, stopping short of it and continuing on the next row. Keep
that exactly: those lines end where IMAGE 3 ends them and must never run
across, under or over the figure. The diagram occupies only the space IMAGE 3
gives it — do not enlarge it into the text, and do not push the text away to
make more room. The page holds no blank rows reserved for the figure."""


# --------------------------------------------------------------------------- #
# Last word — placed AFTER every other block                                   #
# --------------------------------------------------------------------------- #
# Order matters. When the long diagram block was appended after the layout
# rules, the model spaced the writing out and floated it mid-gap: the closing
# instructions carried more weight than the head-line rule buried above them.
# So the one rule that keeps failing is restated last, short and blunt.
FINAL_BASELINE_REMINDER = """
⚠️ LAST AND MOST IMPORTANT — READ THIS AFTER EVERYTHING ELSE ABOVE.

The previous attempt failed on exactly one thing: the writing floated in the
MIDDLE of the gaps, with the printed rules running BETWEEN the rows of text.
That is wrong. Fix it:

1. Every Hindi word's शिरोरेखा (its straight top head-line) is drawn ON a
   printed rule. The head-line and the rule are the SAME line — they touch,
   they overlap, there is NO white gap between them.
2. The letters hang DOWNWARD from that rule into the gap below it. The gap
   BELOW each rule holds the letters; the space ABOVE the rule stays empty
   apart from the odd upper matra.
3. A printed rule must NEVER run between two rows of writing, and must never
   pass through the middle or the bottom of a word.
4. Keep the rows CLOSE together, one row per rule, exactly as IMAGE 3 has
   them. Do not open the line spacing out, and do not centre HINDI writing in
   the gaps.
5. The rules above are for HINDI. A row of pure ENGLISH letters or MATHS
   symbols is the one exception: it sits vertically CENTRED in its gap,
   touching neither rule — exactly where IMAGE 3 puts it.

Before you output the page, check the first three lines: is each Hindi word
hanging from a rule that touches its head-line? If any Hindi row is sitting in
the middle of a gap, move it up onto the rule above it. A pure English/maths
row belongs mid-gap — leave it centred."""
