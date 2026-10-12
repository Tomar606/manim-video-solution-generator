# Designing a part — everything the engine accepts, on one page

Read this instead of the engine. On CHE-C3-SA-06 the designer spent 33 minutes,
of which ~20 went on reading `engine.js`, `build_spec.py` and the gates to learn
what a beat may contain, measuring KaTeX by hand, and writing 34KB of layered
LaTeX. All of that is here, measured, and the LaTeX is generated.

**Your job ends at the route gate.** Write `spec/parts/design_part<N>.json` and
`spec/route_part<N>.json`, run `python3 tools/build_clip.py <slug> run --only
route --part <N>`, report. Do not pre-check what the later gates check —
`bind` (every `say` spoken in its beat, labels named aloud), `spec` (validate +
QA on real pixels) and the storyboard catch it, and say exactly what to fix.

## The frame

| | |
|---|---|
| stage | 1080 x 470 px band above the caption band; everything you place is on it |
| label `x`, `y` | FRACTIONS of the stage (0-1). `center: true` makes `x` the label's centre |
| label size | 46px default (Devanagari sets ~25px/char, ~76px tall); `small: true` = 32px |
| equation box | fits 900 x 420 px, scaled UP to 1.85x at most — a short line reads big, a two-row ladder sets at ~50-61px |
| heading | a label at `x 0.5, y 0.03, center, accent` — sits above the equation with ~23px clear |
| captions | none under `equation` segments (`video.json` `suppress_captions`); diagrams keep theirs |

## A beat

```json
{ "type": "p2-rate",            // unique across ALL parts; prefix "<N>-" in multi-part videos
  "_why": "what the student sees and why — an SVG agent draws diagrams from this alone",
  "cues": [8, 12],              // HeyGen SRT cues it covers (1-based, inclusive)
  ...ONE of: "ladder" | "equation" | "diagram" | "block",
  "labels": [ ... ] }           // optional, with any of them
```

Never a `diagram` and an `equation`/`ladder` in one beat — they share the band.
Cues no beat claims are quiet segments: presenter, captions, clean plate.

**Timing is spoken words, never seconds.** Anything that appears carries
`"say": "<words as the SRT has them>"`, optional `"dt"` (seconds, may be
negative), `"say_n": 2` for a repeat inside the beat; a label's exit is
`"out_say"`. Anchor on a clear word near a formula, not on the formula — the
transcript spells spoken numbers unpredictably.

## Templates

### 1. Ladder — every derivation (सिद्ध कीजिए, व्युत्पन्न, "equation में रख देते हैं")

```json
{ "type": "p4-substitute", "cues": [15, 17],
  "ladder": {
    "rows": [["t", "=", {"frac": ["2.303", "k"]}, "\\log_{10}", {"frac": ["[A]_0", "[A]"]}],
             ["t_{1/2}", "=", {"frac": ["2.303", "k"]}, "\\log_{10}", {"frac": ["[A]_0", ["[A]_0", "/2"]]}]],
    "steps": [{"say": "दोनों", "show": ["0"], "gold": ["0.0", "0.4.1"]},
              {"say": "t half", "show": ["1"], "gold": ["1.0", "1.4.1.1"]},
              {"say": "ऊपर", "strike": ["1.4.0"]},
              {"say": "नीचे", "strike": ["1.4.1.0"]}] } }
```

- A row is a list of LaTeX terms; `{"frac": [num, den]}` is a fraction, and a
  part given as a list splits it (`["[A]_0", "/2"]`).
- Addresses: `"1"` row 1, `"1.4"` its term 4, `"1.4.1"` that fraction's
  denominator, `"1.4.1.0"` the first piece of it.
- Each step: `show` (white) / `gold` (swapped in, the point) / `red` / `strike`
  (red + cancel) / `white` (back to plain). One step = one frame, cross-faded.
- Generated for you: the row being worked on is boxed in gold, earlier rows
  dim, gold and red stay where set, and nothing moves as terms appear.
- Two rows per beat reads best; three at most. Start a new beat for the next
  pair, repeating the last row on top.

### 2. The result, boxed

```json
{ "type": "p8-final", "cues": [25, 26],
  "ladder": { "rows": [["t_{1/2}", "=", {"frac": ["0.693", "k"]}]],
              "steps": [{"say": "मिलेगा", "show": ["0"]},
                        {"say": "ध्यान से देखो", "gold": ["0.2"]}] },
  "labels": [{"text": "प्रारंभिक सान्द्रण मौजूद ही नहीं", "x": 0.5, "y": 0.9,
              "center": true, "accent": true, "say": "प्रारंभिक सान्द्रण", "cue": "मौजूद"}] }
```

### 3. Graph or apparatus built as he explains (SVG)

```json
{ "type": "p1-halflife", "cues": [4, 7],
  "_why": "…where each id sits on the 1080x470 stage, what it looks like…",
  "diagram": { "asset": "assets/svg/p1-halflife.svg",
    "timeline": [{"id": "axes",  "action": "draw",   "say": "अर्द्ध-आयुकाल", "dur": 0.8, "ease": "smooth"},
                 {"id": "curve", "action": "draw",   "say": "किसी अभिक्रिया", "dur": 1.4, "ease": "smooth"},
                 {"id": "dot",   "action": "move",   "say": "आधा भाग", "to": [240, -137], "dur": 1.2},
                 {"id": "mark",  "action": "pop_in", "say": "कर चुका", "dur": 0.4}] },
  "labels": [{"text": "समय", "x": 0.8333, "y": 0.9149, "center": true, "say": "वह समय"},
             {"text": "अभिकारक की सांद्रता", "x": 0.2778, "y": 0.06, "center": true,
              "small": true, "spoken": false, "say": "अर्द्ध-आयुकाल", "dt": 0.6}] }
```

Actions: `draw` (strokes draw on; implies visible), `fade_in`, `pop_in`,
`pulse`, `move` (`to: [dx, dy]` px from its drawn place), `fade_out`,
`pop_out`; each takes `dur`, optional `ease: "smooth"`. Every animated id must
exist in the SVG — list them all; the SVG agent provides exactly these.
`"clear": false` carries the figure into the next beat (`carry_over` there).
Look in `tools/clip/figures/index.json` first and name the closest shipped
figure in `_why` so the SVG agent starts from it.

### 4. Counted list / contrast / heading lines

```json
{ "type": "p6-recap", "cues": [24, 30],
  "block": { "kind": "points", "title": "सक्रियण ऊर्जा", "say": "याद रखना",
             "items": [{"text": "ऊर्जा अवरोध पार करने की न्यूनतम ऊर्जा", "say": "न्यूनतम"},
                       {"text": "Catalyst इसे कम कर सकता है", "say": "catalyst"}] } }
```

`kind: "points"` fills IN — every item stays, the spoken one bright.
`kind: "compare"`: `cards: [{"head", "body", "say"}]`. No `kind`: `lines:
[{"text", "say"}]`. Max ~5 items; each under ~40 characters.

## Labels

`{"text", "x", "y", "center", "small", "accent" (gold), "say", "dt", "out_say",
"spoken": false (part of the figure, never said aloud — arrives with it),
"cue": "<the word in his sentence that names it>"}`. Every spoken label's cue
must be in the caption it lands on (`check_labels.py`). A label in its own
open space needs ~25px per Devanagari character of width at 46px.

## Rules the gates hold you to

- Screen text ORGANISES; it does not repeat the caption. Use his words; no
  symbol on screen before he defines it.
- "No graphic" is a valid beat. A stage that is never quiet means you stopped choosing.
- The question's wording sets the strategy: सिद्ध कीजिए = ladders; सचित्र =
  the figure is the spine; लाभ/कारक/उपाय = a points list.
- Chemistry and physics are SVG-only; every route entry `"route": "svg"`.

`spec/route_part<N>.json`:

```json
{ "beats": [ {"slug": "p2-rate", "route": "svg", "mark": "what is examined",
              "why_drawn": "why a drawing and not a clip"} ] }
```
