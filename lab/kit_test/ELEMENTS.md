# Kit elements and the lessons behind them

The element catalogue for `stage.html` and what the reference edits taught. For what a finished reel must
look like, see [STANDARD.md](STANDARD.md); for the order of work, the `reel` skill.


On 19 Oct 2026 we studied another edit of our own Mohenjo-daro narration
(HIN-SM-02 T01) beat by beat. What it did better is now part of the kit.
What it got wrong is listed here so we don't repeat it.

**New plan pieces**

| Piece | Plan syntax | Use it for |
|---|---|---|
| Presenter size per beat | beat `"presenter": "full"` | Story beats (a walk, a zoom, a reveal). He stands full size even when the plan's `presenter_style` is `card`. Use the card when content needs room, and `hub` for the question and answer moments. |
| Curiosity question | `{"type": "ask", "text": "हवा और रोशनी कहाँ से?", "at": cue, "answer": "…", "t_answer": cue}` | A question on screen before its answer. The answer ticks in underneath it on its cue. |
| Then and now | `{"type": "inset", "src": "<photos path>", "label": "मोहनजोदड़ो", "main_label": "जैसलमेर, आज", "at": cue}` | A framed photo over the full-frame background, with both places named. `side: "left"` flips it. |
| Points tracker | plan `"tracker": {"from": cue}` | The points finished so far, kept in the corner beside the presenter card. Items come from the spine (or `tracker.items` for shorter labels). It shows on card beats only; a beat can turn it off with `"tracker": false`. |

**New compile checks** (`compile.py: gates`)

- **GATE `hook_visual`:** part 1 must open on a Veo clip, not on a title card over a talking head. Later parts only warn. `"hook": "exempt"` turns it off; say why in `_about`.
- **GATE `no_em_dash`:** no screen text may contain an em-dash.
- **WARN `long_hold`:** the picture didn't change for more than `max_hold` seconds (default 6). Every cut, element entrance, list item and inner cue counts as a change. Some holds are right (an answer sheet you want read); most aren't.
- **WARN `dead_air`:** a beat longer than 2 s with no clip and nothing on it.

**Not enforced by code; check these by eye**

- **A generated clip must not show what the answer says is wrong.** The reference edit's street front was full of ground-floor windows, the very misconception it warned against 30 seconds later, and its houses had sloping roofs. Review every clip against the answer before it goes in.
- **Word each point the same way everywhere.** The hero text, the tracker, the recap and the answer sheet must match. Three wordings of one point means the student copies the wrong one.
- **Nothing that imitates something real.** No invented DMs, like counts or commenter names. Use the real thing, or make it plainly illustrative. (Superseded on one point: the years and the question now sit on the exam-sheet photographs the latest reference videos use; see STANDARD.md.)
- **Put the answer page on a clean page, in full exam sentences.** No tilt, and no dark text on texture.

### Elements from the team's reference board (21 Oct 2026)

The team keeps a Pinterest board of green-screen overlays
("resources-for-video-gen"). Each of its groups is now a native kit element,
drawn in the video's own theme and timed to a cue, so nothing has to be keyed
and no licence is in doubt.

| Board group | Element | Plan syntax (cues are line indices or `[line, s]`) | Sound |
|---|---|---|---|
| Search | `search` | `{"type":"search","slot":"upper","text":"वैष्णववाद क्या है?","at":cue}`; it types, then blinks | laptop keys, then a double-click |
| Buttons | `toggle` | `{"type":"toggle","slot":"upper","text":"रक्षक","at":cue,"t_on":cue}` | light-button press |
| Question mark | `qmarks` | `{"type":"qmarks","at":cue,"n":10}`; seeded, so every render matches | soft pops |
| Timeline | `timeline` | `{"type":"timeline","slot":"upper","items":[["320 ई.","गुप्त वंश",cue], ...]}` | a node click per year |
| Loading | `progress` | `{"type":"progress","slot":"upper","value":90,"text":"syllabus पूरा","at":cue}` | clock ticks while it fills, a tick at the end |
| Tick/Cross | `verdict` | `{"type":"verdict","kind":"cross"\|"tick","x":300,"y":520,"at":cue}` | a metal hit on a cross, a tick on a tick |
| UI Cards | `notify` | `{"type":"notify","slot":"upper","items":[["1","title","body",cue], ...]}` | a card slide per card |
| Circle animation | `ring` | `{"type":"ring","x":330,"y":560,"w":420,"h":360,"label":"अधर्म","at":cue}`: a marker circle drawn round a region of the frame | a scribble |
| Markings | `pins` | `{"type":"pins","items":[[x,y,"मथुरा",cue], ...]}` | a pin drop each |
| Paper Texture | `paper` | `{"type":"paper","slot":"upper","text":"…","at":cue}`: a torn, taped notepad slip | a page flip and tape |
| Bg | plates | `"plate": "grid-ember"` or `"grid-graphite"` | none |

The board's "History" group (an India map with a glowing outline) is not
rebuilt as an element. Use `tools/make_sea_map.py` (coastline only), so that
India's de facto boundary is never drawn.

**Sounds added from the team's SFX zip:** five Mixkit cuts, each measured
against the library rules and recorded in `library/sfx/manifest.json`:
`button-press/double-click`, `button-press/light-button`, `clock/tick-tock`,
`page-turn/book-page-flip` and `stamp/metal-hit`. The correct-answer chime was
rejected as tonal (the ringtone family) and the arrow shot as a rising whistle.
The zip's four compilation MP3s, ripped from YouTube and Instagram videos, were
not imported: their licence is unknown.

**Free-licensed originals (21 Oct 2026).** The board's own pins mostly come from
paid stock (Adobe Stock, VideoHive) or from other creators, so none of them is
used. For an animated, stock-like look instead:

- **`lottie` element:** free animations from LottieFiles (Lottie Simple
  License: commercial use, no credit), kept in `library/elements/lottie/` with
  `manifest.json` (source, author, id, licence). Each was checked to carry no text
  layer. Usage: `{"type":"lottie","src":"tick-spark","x":760,"y":560,"w":520,"at":cue}`;
  `slot` can replace `x`/`y`, `"loop": true` repeats it, and `"colour": "#fff"`
  or `"var(--accent)"` recolours it. Many files carry padding inside their
  canvas, so size them with `w`; the frame-edge check catches one set too large.
  The renderer is seeked, so these stay deterministic. Available:
  - ticks and crosses: tick-spark, tick-circle, tick-badge, cross-circle, cross-bold;
  - pins and circles: pin-ripple, pin-blue, circle-teal, circle-sketch;
  - arrows: arrow-loop, arrow-dashed;
  - search and toggles: magnifier, toggle-dark, toggle-blue;
  - question marks: question-green, question-navy;
  - charts: growth-blue, growth-green;
  - notifications and notes: notify-phone, chat, clipboard.
  Each plays a sound chosen from its name.
- **Paper textures:** `library/elements/textures/` (ambientCG, CC0). Use
  `"texture": "crumpled" | "kraft" | "kraft-dark"` on the `paper` element.
- **Further free sources, if more are needed:** LottieFiles (search API
  `graphql.lottiefiles.com`), ambientCG and Poly Haven (CC0 textures), Kenney
  (CC0 UI), Mixkit (free SFX and video). Pixabay and Pexels need an API key.
